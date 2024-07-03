import os
from autogen import AssistantAgent, UserProxyAgent, ConversableAgent, GroupChat, GroupChatManager
# from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
# from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

llm_config = {"model": "gemini-1.5-flash", "api_key":"AIzaSyAHNdDCfn5_lAqtw0QUdnmbhMFc6izHRJk", "api_type": "google"}
assistant = AssistantAgent("assistant", 
                           llm_config=llm_config, 
                           system_message="Your role is to put together clearly what are the firewall configurations that needs to be added or removed and write code or scripts to execute them")

explorer = AssistantAgent("explorer", 
                          llm_config=llm_config, 
                          system_message="Your role is to identify what are the possible IP addressed that might be related to the IP address given for configuration")

cleaner = AssistantAgent("cleaner",
                         llm_config=llm_config,
                         system_message= "Your role is to check for duplicates in the firewall configurations and ensure that the newly added configurations is truly necessary."

)

planner = AssistantAgent("planner", 
                         llm_config=llm_config,
                         system_message=''' Your role is to deligate work to the various agents and help them communicate with one another. You should be aware of the other agent's role. 
                         explorer: Identify other possible IP addresses that are related to the given IP address. 
                         cleaner: Ensure that the list of configurations are not messy. 
                         assistant: put together and give human the final output (code)
                         user_proxy: executing code, you will be asking user_proxy to speak if you need more information from the human. 
                         You will be assigning these agents work and ensure that this is a well-oiled machine to give user the best output possible.  
                         When in doubt do not make assumption, ask human.
                         '''
                         )


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


groupchat = GroupChat(agents=[user_proxy, planner, explorer, cleaner, assistant ], messages=[], speaker_selection_method="auto")

manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config, code_execution_config={"work_dir": "Output","use_docker": False})

planner.reset()
cleaner.reset()
explorer.reset()
assistant.reset()
user_proxy.reset()

# Start the chat
user_proxy.initiate_chat(
    manager,
    message="I am connected to a network swtich via a TCP connection, I would like you to configure the firewall for this switch. "
)

