from autogen import AssistantAgent, UserProxyAgent, config_list_from_json, GroupChat, GroupChatManager

llm_config = {"model": "gemini-1.5-flash", "api_key":"AIzaSyAHNdDCfn5_lAqtw0QUdnmbhMFc6izHRJk", "api_type": "google"}

user_proxy = UserProxyAgent(
   name="Admin",
   system_message="A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved "
                  "by this admin.",
   #max_consecutive_auto_reply=2,
   code_execution_config={
        "work_dir": "Output",
        "use_docker": False,  # Set use_docker to False
    },
)

executor = AssistantAgent(
    name="Executor",
    system_message="Executor. Execute the code written by the engineer and report the result.",
    #max_consecutive_auto_reply=2,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "Output",
        "use_docker": False,  # Set use_docker to False
    },
)

engineer = AssistantAgent(
    name="Engineer",
    llm_config=llm_config,
    system_message='''Engineer. You follow an approved plan. You write python/shell code to solve tasks. You are
    and expert developing scripts that run on raspberry pi zero 2w. Wrap the 
    code in a code block that specifies the script type. The user can't modify your code. So do not suggest 
    incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by 
    the executor. Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. 
    Check the execution result returned by the executor. If the result indicates there is an error, fix the error and 
    output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed 
    or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your 
    assumption, collect additional info you need, and think of a different approach to try.''',
)

planner = AssistantAgent(
    name="Planner",
    system_message='''Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin 
    approval. The plan may involve an engineer who can write code and an executor and critic who doesn't write code. 
    Explain the plan first. Be clear which step is performed by an engineer, executor, and critic.''',
    llm_config=llm_config,
)

critic = AssistantAgent(
    name="Critic",
    system_message="Critic. Double check plan, claims, code from other agents and provide feedback.",
    llm_config=llm_config,
)

groupchat = GroupChat(agents=[user_proxy, engineer,executor, planner, critic], messages=[], max_round=10)
manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config, code_execution_config={"work_dir": "Output","use_docker": False})

user_proxy.initiate_chat(manager, message=''' i want to perform log sanitisation on the file''')