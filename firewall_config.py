import os
from autogen import AssistantAgent, UserProxyAgent, ConversableAgent, GroupChat, GroupChatManager
# from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
# from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

llm_config = {"model": "gemini-1.5-flash", "api_key":"AIzaSyAHNdDCfn5_lAqtw0QUdnmbhMFc6izHRJk", "api_type": "google"}
assistant = AssistantAgent("assistant", 
                           llm_config=llm_config, 
                           system_message="Your role is to put write a python script to perform firewall configuration on a windows laptop")


## Possible to include another RAG agent
# info_bank = RetrieveUserProxyAgent(
#     name="info_bank", 
#     human_input_mode="NEVER",
#     max_consecutive_auto_reply=3,
#     retrieve_config={
#         "task": "code",
#         "docs_path": "https://raw.githubusercontent.com/microsoft/FLAML/main/website/docs/Examples/Integrate%20-%20Spark.md",
#         "chunk_token_size": 1000,
#         "model": config_list[0]["model"],
#         "collection_name": "groupchat",
#         "get_or_create": True,
#     },
#     code_execution_config=False,  # we don't want to execute code in this case.
#     description="Assistant who has extra content retrieval power for solving difficult problems.",
# )

user_proxy = UserProxyAgent("user_proxy", code_execution_config={"last_n_messages": 2, "work_dir": "coding",}, human_input_mode="ALWAYS", 
                           )

# Start the chat
user_proxy.initiate_chat(
    assistant,
    message="I wan to configure firewall for windows. "
)

