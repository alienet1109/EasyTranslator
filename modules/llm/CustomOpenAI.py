from .BaseLLM import BaseLLM
from openai import OpenAI


class CustomOpenAI(BaseLLM):
    """
    通用 OpenAI 兼容接口模型
    通过自定义 base_url / api_key / model_name 调用任意 OpenAI 兼容后端。
    """

    def __init__(self, base_url: str, api_key: str, model: str):
        super(CustomOpenAI, self).__init__()
        # OpenAI Python SDK v1 风格客户端
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model
        self.messages = []

    def initialize_message(self):
        self.messages = []

    def ai_message(self, payload):
        self.messages.append({"role": "assistant", "content": payload})

    def system_message(self, payload):
        self.messages.append({"role": "system", "content": payload})

    def user_message(self, payload):
        self.messages.append({"role": "user", "content": payload})

    def get_response(self, temperature: float = 0.8):
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.messages,
            temperature=temperature,
            top_p=0.8,
        )
        return completion.choices[0].message.content

    def chat(self, text: str, temperature: float = 0.8):
        self.initialize_message()
        self.user_message(text)
        response = self.get_response(temperature=temperature)
        return response

    def print_prompt(self):
        for message in self.messages:
            print(message)

