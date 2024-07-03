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
        "docs_path": "https://raw.githubusercontent.com/microsoft/autogen/main/README.md",
    },
)

assistant.reset()
ragproxyagent.initiate_chat(assistant, message=ragproxyagent.message_generator, problem="What is autogen?")




# from autogen import OpenAIWrapper

# client = OpenAIWrapper(api_key="AIzaSyAHNdDCfn5_lAqtw0QUdnmbhMFc6izHRJk", api_type="google")
# # Completion
# response = client.create(messages=[{"role": "user", "content": "Python learning tips."}], model="gemini-1.5-flash")
# # extract the response text
# print(client.extract_text_or_completion_object(response))









# import os
# from flask import Flask, request, jsonify, send_from_directory
# from autogen import AssistantAgent, UserProxyAgent

# app = Flask(__name__, static_folder='../static', static_url_path='')
# llm_config = {"model": "gemini-1.5-flash", "api_key": "AIzaSyAHNdDCfn5_lAqtw0QUdnmbhMFc6izHRJk", "api_type": "google"}
# assistant = AssistantAgent("assistant", 
#                            system_message="Explain the code that you are writing too and provide the code to do so",
#                            llm_config=llm_config)
# user_proxy = UserProxyAgent("user_proxy", code_execution_config={"last_n_messages": 2, "work_dir": "coding"})

# @app.route('/chat', methods=['POST'])
# def chat():
#     user_message = request.json.get('message')
#     print(f"Received message: {user_message}")  # Log the received message
    
#     try:
#         # Start the conversation with user's message
#         response = user_proxy.initiate_chat(assistant, message=user_message)
        


#         print(f"Response from initiate_chat: {response}")  # Log the raw response

#         # Ensure the response is properly formatted
#         if hasattr(response, 'choices'):
#             response_text = response.choices[0].message.content
#         else:
#             response_text = "Unexpected response format."

#         # Prepare the messages to be returned
#         messages = [
#             {"sender": "user", "message": user_message},
#             {"sender": "bot", "message": response_text}
#         ]

#         return jsonify({"messages": messages})

#     except Exception as e:
#         print(f"Error during chat: {e}")
#         return jsonify({"messages": [{"sender": "error", "message": str(e)}]})

# @app.route('/')
# def serve_static_index():
#     print(f"Serving static file from {app.static_folder}/index.html")
#     return send_from_directory(app.static_folder, 'index.html')

# @app.route('/<path:path>')
# def serve_static_files(path):
#     print(f"Serving static file: {path}")
#     return send_from_directory(app.static_folder, path)

# if __name__ == '__main__':
#     app.run(debug=True)
