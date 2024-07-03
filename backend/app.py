import os
import threading
from itertools import chain

import gradio_UI as gr
from autogen import AssistantAgent, UserProxyAgent
from autogen.code_utils import extract_code

# Replace with your actual API key and model
llm_config = {"model": "gemini-1.5-flash", "api_key": "AIzaSyAHNdDCfn5_lAqtw0QUdnmbhMFc6izHRJk", "api_type": "google"}

# Initialize agents
def initialize_agents():
    assistant = AssistantAgent(
        name="assistant",
        system_message="Explain the code that you are writing too and provide the code to do so",
        llm_config=llm_config
    )

    user_proxy = UserProxyAgent(
        name="user_proxy",
        code_execution_config={"last_n_messages": 2, "work_dir": "coding"}
    )

    return assistant, user_proxy

assistant, user_proxy = initialize_agents()

# Function to handle progressive updates
def handle_user_message(user_message):
    user_proxy.initiate_chat(assistant, message=user_message)
    messages = user_proxy.chat_messages[assistant]
    response_messages = []
    for message in messages:
        response_messages.append({"sender": "bot", "message": message.get("content", "")})
    return response_messages

def chatbot_response(user_message, chat_history):
    try:
        response_messages = handle_user_message(user_message)
        chat_history.append({"sender": "user", "message": user_message})
        chat_history.extend(response_messages)
        return chat_history
    except Exception as e:
        return chat_history + [{"sender": "error", "message": str(e)}]

def get_description_text():
    return """
    A chatbot for autogen model 
    """

with gr.Blocks() as demo:
    description = gr.Markdown(get_description_text())

    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        bubble_full_width=False,
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

    def respond(message, chat_history):
        return chatbot_response(message, chat_history)

    chatiface = gr.ChatInterface(
        fn=respond,
        chatbot=chatbot,
        textbox=txt_input,
        examples=[
            ["write a python function to count the sum of two numbers?"],
            ["what if the production of two numbers?"],
            [
                "Plot a chart of the last year's stock prices of Microsoft, Google and Apple and save to stock_price.png."
            ],
            ["show file: stock_price.png"],
        ],
    )

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")
