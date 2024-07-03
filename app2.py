import os
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='../static', static_url_path='')

# Sample configuration for the assistant (you can replace this with your own setup)
llm_config = {"model": "gemini-1.5-flash", "api_key": "your_api_key_here", "api_type": "google"}

@app.route('/')
def serve_static_index():
    print(f"Serving static file from {app.static_folder}/index.html")
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    print(f"Received message: {user_message}")  # Log the received message
    
    try:
        # Simulate a response from an assistant based on the user's message
        response_text = f"This is a response to '{user_message}' from the assistant."

        # Prepare the messages to be returned
        messages = [
            {"sender": "user", "message": user_message},
            {"sender": "bot", "message": response_text}
        ]

        return jsonify({"messages": messages})

    except Exception as e:
        print(f"Error during chat: {e}")
        return jsonify({"messages": [{"sender": "error", "message": str(e)}]})

if __name__ == '__main__':
    app.run(debug=True)
