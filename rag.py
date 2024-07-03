import autogen
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

llm_config = {"model": "gemini-1.5-flash", "api_key":"AIzaSyAHNdDCfn5_lAqtw0QUdnmbhMFc6izHRJk", "api_type": "google"}

assistant = RetrieveAssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant.",
    llm_config=llm_config,
)

ragproxyagent = RetrieveUserProxyAgent(
    name="ragproxyagent",
    retrieve_config={
        "task": "qa",
        "docs_path": "https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/",
    },
)

assistant.reset()
ragproxyagent.initiate_chat(assistant, message=ragproxyagent.message_generator, problem="What is autogen?")