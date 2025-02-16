import anthropic
from .BaseLLM import BaseLLM

class Claude(BaseLLM):

    def __init__(self, model="claude-3-5-sonnet-20240620"):
        super(Claude, self).__init__()
        self.model_name = model
        self.client = anthropic.Anthropic(
            # defaults to os.environ.get("ANTHROPIC_API_KEY")
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

# def lang_detect(text):
#     import re
#     def count_chinese_characters(text):
#         # 使用正则表达式匹配所有汉字字符
#         chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
#         return len(chinese_chars)
            
#     if count_chinese_characters(text) > len(text) * 0.05:
#         lang = 'zh'
#     else:
#         lang = 'en'
#     return lang


# def extract_json(text, **kwargs):

#     try:
#         # Use regular expressions to find all content within curly braces
#         json_objects = re.findall(r'(\{[^{}]*\}|\[[^\[\]]*\])', text, re.DOTALL)
        
#         valid_jsons = []
        
#         for obj in json_objects:
#             try:
#                 # Attempt to parse each JSON object
#                 parsed_json = json.loads(obj) #(obj.replace("'", "\""))  # Replace single quotes with double quotes
#                 valid_jsons.append(parsed_json)
#             except json.JSONDecodeError:
#                 continue

#         assert(len(valid_jsons) == 1, f"Found {len(valid_jsons)} JSON objects in the text: {valid_jsons}")
#         return valid_jsons[0]
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         print('Error parsing response: ', text)
#         #import pdb; pdb.set_trace()
        
#         return False

# def get_response_json(post_processing_funcs=[extract_json], **kwargs):
    
#     nth_generation = 0

#     while (True):
#         response = get_response(**kwargs, nth_generation=nth_generation)
        
#         for post_processing_func in post_processing_funcs:
#             response = post_processing_func(response, **kwargs)
#         #print(f'parse results: {json_response}')
#         json_response = response 
        
#         if json_response:
#             break 
#         else:
#             nth_generation += 1
#             if nth_generation > 12:
#                 import pdb; pdb.set_trace()
                
#                 break    

    
#     return json_response
    
if __name__ == '__main__':
    messages = [{"role": "system", "content": "Hello, how are you?"}]
    model = "claude-3-5-sonnet-20240620"
    #model = 'gpt-4o'
    llm = Claude()
    
    print(llm.chat("Say it is a test."))
        

