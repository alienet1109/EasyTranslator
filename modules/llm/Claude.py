import anthropic
import os
from .BaseLLM import BaseLLM

class Claude(BaseLLM):

    def __init__(self, model="claude-3-5-sonnet-20240620"):
        super(Claude, self).__init__()
        self.model_name = model
        self.client = anthropic.Anthropic(
            api_key = os.environ.get("ANTHROPIC_API_KEY")
        )
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

    def get_response(self):
        message = self.client.messages.create(
            model=self.model_name,
            max_tokens=4096,
            messages=self.messages
        )
        return message.content

    def chat(self,text):
        self.initialize_message()
        if isinstance(messages, str):
            self.user_message(text)
            response = self.get_response()
        return response
    
    def print_prompt(self):
        for message in self.messages:
            print(message)
            
if __name__ == '__main__':
    messages = [{"role": "system", "content": "Hello, how are you?"}]
    model = "claude-3-5-sonnet-20240620"
    #model = 'gpt-4o'
    llm = Claude()
    
    print(llm.chat("Say it is a test."))
        

