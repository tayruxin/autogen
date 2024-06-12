import os
from autogen import AssistantAgent, UserProxyAgent
import google.generativeai as genai
import autogen

genai.configure(api_key ="AIzaSyAHNdDCfn5_lAqtw0QUdnmbhMFc6izHRJk")
llm_config = {"model": "gemini-1.5-flash", "api_key":"AIzaSyAHNdDCfn5_lAqtw0QUdnmbhMFc6izHRJk", "api_type": "google"}

# llm_config = {"model": "llama2-chat-7B", "base_url": "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-chat-hf"}

assistant = AssistantAgent(
    name="assistant", 
    llm_config=llm_config)

pm = AssistantAgent(
    name="pm", 
    system_message="You will help break down the initial idea into a well scoped requirement for the assistant; Do not involve in future conversation or error fixing ",
    llm_config=llm_config)

user_proxy = UserProxyAgent(
    name="user_proxy", 
    system_message="A human admin who will give the idea and run the code provided by the assistant",
    code_execution_config={"last_n_messages": 2, "work_dir": "coding"},
    human_input_mode="ALWAYS"
    )

# user_proxy = UserProxyAgent("user_proxy", code_execution_config=False)

# Create group chat 
groupchat = autogen.GroupChat(
    agents=[user_proxy, assistant, pm], messages=[])

manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# Start the chat
user_proxy.initiate_chat(
    manager,
    message= "build a classic & basic ping pong game with 2 players in python"
)
