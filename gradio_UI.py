import gradio as gr
import time
import google.generativeai as genai

GOOGLE_API_KEY = "AIzaSyAHNdDCfn5_lAqtw0QUdnmbhMFc6izHRJk"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

chat = model.start_chat(history=[])

# Transform Gradio history to Gemini format
def transform_history(history):
    new_history = []
    for chat in history:
        new_history.append({"parts": [{"text": chat[0]}], "role": "user"})
        new_history.append({"parts": [{"text": chat[1]}], "role": "model"})
    return new_history

def response(message, history):
    global chat
    # The history will be the same as in Gradio, the 'Undo' and 'Clear' buttons will work correctly.
    chat.history = transform_history(history)
    response = chat.send_message(message)
    response.resolve()

    # Each character of the answer is displayed
    for i in range(len(response.text)):
        time.sleep(0.05)
        yield response.text[: i+1]

gr.ChatInterface(response,
                 title='Gemini Chat',
                 theme="Soft",
                 textbox=gr.Textbox(placeholder="Question to Gemini"),
                 retry_btn=None).launch(debug=True)