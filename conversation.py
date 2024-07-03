import os

from autogen import ConversableAgent

llm_config = {"model": "gemini-1.5-flash", "api_key":"AIzaSyAHNdDCfn5_lAqtw0QUdnmbhMFc6izHRJk", "api_type": "google"}

student_agent = ConversableAgent(
    name="Student_Agent",
    system_message="You are a student willing to learn.",
    llm_config=llm_config,
)
teacher_agent = ConversableAgent(
    name="Teacher_Agent",
    system_message="You are a math teacher.",
    llm_config=llm_config,
)

chat_result = student_agent.initiate_chat(
    teacher_agent,
    message="What is triangle inequality?",
    summary_method="reflection_with_llm",
    max_turns=2,
)