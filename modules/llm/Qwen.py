from .BaseLLM import BaseLLM
from peft import PeftModel
from openai import OpenAI
import os
from transformers import AutoModelForCausalLM, AutoTokenizer

class Qwen(BaseLLM):

    def __init__(self, model="qwen-max"):
        # qwen-max, qwen-plus, qwen-turbo
        super(Qwen, self).__init__()
        self.client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"), 
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
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


class Qwen_local(BaseLLM):
    def __init__(self, model="qwen2.5-7B", adapter_path = None):
        super(Qwen_local, self).__init__()
        model_name = "qwen/Qwen2.5-7B-Instruct"
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto",
            
        )
        if isinstance(adapter_path,str):
            self.model = PeftModel.from_pretrained(self.model, adapter_path)
        elif isinstance(adapter_path,list):
            for path in adapter_path:
                self.model = PeftModel.from_pretrained(self.model, path)
            
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
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
    
        text = self.tokenizer.apply_chat_template(
                self.messages,
                tokenize=False,
                add_generation_prompt=True
            )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=512
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return response
    
    def chat(self,text,temperature = 0.8):
        self.initialize_message()
        self.user_message(text)
        response = self.get_response(temperature = temperature)
        return response
    
    def print_prompt(self):
        for message in self.messages:
            print(message)