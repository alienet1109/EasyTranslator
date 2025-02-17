from .BaseLLM import BaseLLM
from openai import OpenAI
import os

class LangChainGPT(BaseLLM):

    def __init__(self, model="gpt-4o-mini"):
        super(LangChainGPT, self).__init__()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = model
        # add api_base        
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
    
    def chat(self,text,temperature = 0.8):
        self.initialize_message()
        self.user_message(text)
        response = self.get_response(temperature = temperature)
        return response
    
    def print_prompt(self):
        for message in self.messages:
            print(message)


