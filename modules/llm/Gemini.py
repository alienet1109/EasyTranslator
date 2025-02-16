from .BaseLLM import BaseLLM
import google.generativeai as genai
import os
import time

class Gemini(BaseLLM):
    def __init__(self, model="gemini-1.5-flash"):
        super(Gemini, self).__init__()
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_name = model
        self.model = genai.GenerativeModel(model)
        self.messages = []


    def initialize_message(self):
        self.messages = []

    def ai_message(self, payload):
        self.messages.append({"role": "model", "parts": payload})

    def system_message(self, payload):
        self.messages.append({"role": "system", "parts": payload})

    def user_message(self, payload):
        self.messages.append({"role": "user", "parts": payload})

    def get_response(self,temperature = 0.8):
        time.sleep(3)
        chat = self.model.start_chat(
            history = self.messages
        )
        response = chat.send_message(generation_config=genai.GenerationConfig(
        temperature=temperature,
        ))
        
        return response.text
    
    def chat(self,text):
        chat = self.model.start_chat()
        response = chat.send_message(text)
        return response.text
    
    def print_prompt(self):
        for message in self.messages:
            print(message)