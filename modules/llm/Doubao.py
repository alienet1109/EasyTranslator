from .BaseLLM import BaseLLM
from volcenginesdkarkruntime import Ark
import os

class Doubao(BaseLLM):
    
    def __init__(self, model="ep-20241228220355-cqxcs"):
        super(Doubao, self).__init__()
        self.client = Ark(api_key=os.environ.get("ARK_API_KEY"))
        self.model_name = model
        self.messages = []

    def initialize_message(self):
        self.messages = []

    def ai_message(self, payload):
        self.messages.append({"role": "ai", "content": payload})

    def system_message(self, payload):
        self.messages.append({"role": "system", "content": payload})

    def user_message(self, payload):
        self.messages.append({"role": "user", "content": payload})

    def get_response(self,temperature = 0.8):
    
        completion = self.client.chat.completions.create(
        model=self.model_name,
        messages=self.messages,
        temperature=temperature,
        top_p=0.8
        )

        return completion.choices[0].message.content
    
    def chat(self,text):
        self.initialize_message()
        self.user_message(text)
        response = self.get_response()
        return response
    
    def print_prompt(self):
        for message in self.messages:
            print(message)