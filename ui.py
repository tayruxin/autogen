import os
import sys
import threading
from itertools import chain

import anyio
import autogen
import gradio as gr
from autogen import Agent, AssistantAgent, OpenAIWrapper, UserProxyAgent
from autogen.code_utils import extract_code
from gradio import ChatInterface, Request
from gradio.helpers import special_args

LOG_LEVEL = "INFO"
TIMEOUT = 60

llm_config = {
    "model": "gemini-1.5-flash",
    "api_key": "AIzaSyAHNdDCfn5_lAqtw0QUdnmbhMFc6izHRJk",
    "api_type": "google"
}


class myChatInterface(ChatInterface):
    async def _submit_fn(
        self,
        message: str,
        history_with_input: list[list[str | None]],
        request: Request,
        *args,
    ) -> tuple[list[list[str | None]], list[list[str | None]]]:
        history = history_with_input[:-1]
        inputs, _, _ = special_args(self.fn, inputs=[message, history, *args], request=request)

        if self.is_async:
            await self.fn(*inputs)
        else:
            await anyio.to_thread.run_sync(self.fn, *inputs, limiter=self.limiter)

        return history, history


with gr.Blocks() as demo:

    def flatten_chain(list_of_lists):
        return list(chain.from_iterable(list_of_lists))

    class thread_with_trace(threading.Thread):
        # https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/
        # https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread
        def __init__(self, *args, **keywords):
            threading.Thread.__init__(self, *args, **keywords)
            self.killed = False
            self._return = None

        def start(self):
            self.__run_backup = self.run
            self.run = self.__run
            threading.Thread.start(self)

        def __run(self):
            sys.settrace(self.globaltrace)
            self.__run_backup()
            self.run = self.__run_backup

        def run(self):
            if self._target is not None:
                self._return = self._target(*self._args, **self._kwargs)

        def globaltrace(self, frame, event, arg):
            if event == "call":
                return self.localtrace
            else:
                return None

        def localtrace(self, frame, event, arg):
            if self.killed:
                if event == "line":
                    raise SystemExit()
            return self.localtrace

        def kill(self):
            self.killed = True

        def join(self, timeout=0):
            threading.Thread.join(self, timeout)
            return self._return

    def update_agent_history(recipient, messages, sender, config):
        if config is None:
            config = recipient
        if messages is None:
            messages = recipient._oai_messages[sender]
        message = messages[-1]
        message.get("content", "")
        return False, None  # required to ensure the agent communication flow continues

    def _is_termination_msg(message):
        """Check if a message is a termination message.
        Terminate when no code block is detected. Currently only detect python code blocks.
        """
        if isinstance(message, dict):
            message = message.get("content")
            if message is None:
                return False
        cb = extract_code(message)
        contain_code = False
        for c in cb:
            if c[0] == "python":
                contain_code = True
                break
        return not contain_code

    def initialize_agents(config_list):
        assistant = AssistantAgent(
            name="assistant",
            max_consecutive_auto_reply=5,
            llm_config=llm_config,  # Use the predefined llm_config
        )

        userproxy = UserProxyAgent(
            name="userproxy",
            human_input_mode="ALWAYS",
            is_termination_msg=_is_termination_msg,
            max_consecutive_auto_reply=1,
            code_execution_config={
                "work_dir": "coding",
                "use_docker": False,
            }    
        )

        return assistant, userproxy

    def chat_to_oai_message(chat_history):
        """Convert chat history to OpenAI message format."""
        messages = []
        if LOG_LEVEL == "DEBUG":
            print(f"chat_to_oai_message: {chat_history}")
        for msg in chat_history:
            messages.append(
                {
                    "content": msg[0].split()[0] if msg[0].startswith("exitcode") else msg[0],
                    "role": "user",
                }
            )
            messages.append({"content": msg[1], "role": "assistant"})
        return messages

    def oai_message_to_chat(oai_messages, sender):
        """Convert OpenAI message format to chat history."""
        chat_history = []
        messages = oai_messages[sender]
        if LOG_LEVEL == "DEBUG":
            print(f"oai_message_to_chat: {messages}")
        for i in range(0, len(messages), 2):
            chat_history.append(
                [
                    messages[i]["content"],
                    messages[i + 1]["content"] if i + 1 < len(messages) else "",
                ]
            )
        return chat_history

    def agent_history_to_chat(agent_history):
        """Convert agent history to chat history."""
        chat_history = []
        for i in range(0, len(agent_history), 2):
            chat_history.append(
                [
                    agent_history[i],
                    agent_history[i + 1] if i + 1 < len(agent_history) else None,
                ]
            )
        return chat_history

    def initiate_chat(config_list, user_message, chat_history):
        if LOG_LEVEL == "DEBUG":
            print(f"chat_history_init: {chat_history}")
        if not llm_config.get("api_key"):  # Check if api_key is present in llm_config
            chat_history.append(
                [
                    user_message,
                    "Hi, nice to meet you! Please ensure your API keys are set correctly in the code.",
                ]
            )
            return chat_history

        assistant.reset()
        oai_messages = chat_to_oai_message(chat_history)
        assistant._oai_system_message_origin = assistant._oai_system_message.copy()
        assistant._oai_system_message += oai_messages

        try:
            userproxy.initiate_chat(assistant, message=user_message)
            messages = userproxy.chat_messages
            chat_history += oai_message_to_chat(messages, assistant)
        except Exception as e:
            chat_history.append([user_message, str(e)])

        assistant._oai_system_message = assistant._oai_system_message_origin.copy()
        if LOG_LEVEL == "DEBUG":
            print(f"chat_history: {chat_history}")
        return chat_history

    def chatbot_reply_thread(input_text, chat_history, config_list):
        """Chat with the agent through terminal."""
        thread = thread_with_trace(target=initiate_chat, args=(config_list, input_text, chat_history))
        thread.start()
        try:
            messages = thread.join(timeout=TIMEOUT)
            if thread.is_alive():
                thread.kill()
                thread.join()
                messages = [
                    input_text,
                    "Timeout Error: Please check your API keys and try again later.",
                ]
        except Exception as e:
            messages = [
                [
                    input_text,
                    str(e) if len(str(e)) > 0 else "Invalid Request to OpenAI, please check your API keys.",
                ]
            ]
        return messages

    def chatbot_reply_plain(input_text, chat_history, config_list):
        """Chat with the agent through terminal."""
        try:
            messages = initiate_chat(config_list, input_text, chat_history)
        except Exception as e:
            messages = [
                [
                    input_text,
                    str(e) if len(str(e)) > 0 else "Invalid Request to OpenAI, please check your API keys.",
                ]
            ]
        return messages

    def chatbot_reply(input_text, chat_history, config_list):
        """Chat with the agent through terminal."""
        return chatbot_reply_thread(input_text, chat_history, config_list)

    def get_description_text():
        return """
        # Microsoft AutoGen: Multi-Round Human Interaction Chatbot Demo
        """

    def respond(message, chat_history):
        config_list = [llm_config]  # Use the predefined llm_config
        chat_history[:] = chatbot_reply(message, chat_history, config_list)
        if LOG_LEVEL == "DEBUG":
            print(f"return chat_history: {chat_history}")
        return ""

    config_list, assistant, userproxy = [llm_config], None, None  # Use the predefined llm_config
    assistant, userproxy = initialize_agents(config_list)

    description = gr.Markdown(get_description_text())

    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        bubble_full_width=False,
        avatar_images=(
            "human.png",
            (os.path.join(os.path.dirname(__file__), "autogen.png")),
        ),
        render=False,
        height=600,
    )

    txt_input = gr.Textbox(
        scale=4,
        show_label=False,
        placeholder="Enter text and press enter",
        container=False,
        render=False,
        autofocus=True,
    )

    chatiface = myChatInterface(
        respond,
        chatbot=chatbot,
        textbox=txt_input,
        examples=[
            ["write a python function to count the sum of two numbers?"],
            ["Help me perform log sanitization"],
            [
                "Plot a chart of the last year's stock prices of Microsoft, Google and Apple and save to stock_price.png."
            ],
            ["show file: stock_price.png"],
        ],
    )


if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")