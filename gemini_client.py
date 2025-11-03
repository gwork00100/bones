from vertexai.language_models import ChatModel
import vertexai
from google.oauth2 import service_account

def start_gemini_chat():
    credentials = service_account.Credentials.from_service_account_file("vertex_key.json")
    
    vertexai.init(
        project="planar-outlook-468600-d0",
        location="us-central1",
        credentials=credentials
    )

    chat_model = ChatModel.from_pretrained("chat-bison")
    chat = chat_model.start_chat()
    
    response = chat.send_message("Hello, Gemini! What can you do?")
    print(response.text)

if __name__ == "__main__":
    start_gemini_chat()
