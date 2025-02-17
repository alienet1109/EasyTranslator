import openai
import requests
import random
import json
from hashlib import md5
from os import path as osp
import os
import csv
import threading

MODEL_NAME_DICT = {
    "gpt-4":"openai/gpt-4",
    "gpt-4o":"openai/gpt-4o",
    "gpt-4o-mini":"openai/gpt-4o-mini",
    "gpt-3.5-turbo":"openai/gpt-3.5-turbo",
    "deepseek-r1":"deepseek/deepseek-r1",
    "deepseek-v3":"deepseek/deepseek-chat",
    "gemini-2":"google/gemini-2.0-flash-001",
    "gemini-1.5":"google/gemini-flash-1.5",
    "llama3-70b": "meta-llama/llama-3.3-70b-instruct",
    "qwen-turbo":"qwen/qwen-turbo",
    "qwen-plus":"qwen/qwen-plus",
    "qwen-max":"qwen/qwen-max",
    "qwen-2.5-72b":"qwen/qwen-2.5-72b-instruct",
    "claude-3.5-sonnet":"anthropic/claude-3.5-sonnet",
    "phi-4":"microsoft/phi-4",
}

def get_models(model_name):
    # return the combination of llm, embedding and tokenizer
    if os.getenv("OPENROUTER_API_KEY", default="") and "YOUR" not in os.getenv("OPENROUTER_API_KEY", default="") and model_name in MODEL_NAME_DICT:
        from modules.llm.OpenRouter import OpenRouter
        return OpenRouter(model=MODEL_NAME_DICT[model_name])
    elif model_name == 'openai':
        from modules.llm.LangChainGPT import LangChainGPT
        return LangChainGPT()
    elif model_name.startswith('gpt-3.5'):
        from modules.llm.LangChainGPT import LangChainGPT
        return LangChainGPT(model="gpt-3.5-turbo")
    elif model_name == 'gpt-4':
        from modules.llm.LangChainGPT import LangChainGPT
        return LangChainGPT(model="gpt-4")
    elif model_name == 'gpt-4o':
        from modules.llm.LangChainGPT import LangChainGPT
        return LangChainGPT(model="gpt-4o")
    elif model_name == "gpt-4o-mini":
        from modules.llm.LangChainGPT import LangChainGPT
        return LangChainGPT(model="gpt-4o-mini")
    elif model_name.startswith("claude-3-5"):
        from modules.llm.Claude import Claude
        return Claude(model="claude-3-5-sonnet-20241022")
    elif model_name in ["qwen-turbo","qwen-plus","qwen-max"]:
        from modules.llm.Qwen import Qwen
        return Qwen(model = model_name)
    elif model_name.startswith('doubao'):
        from modules.llm.Doubao import Doubao
        return Doubao()
    elif model_name.startswith('gemini-2'):
        from modules.llm.Gemini import Gemini
        return Gemini("gemini-2.0-flash")
    elif model_name.startswith('gemini-1.5'):
        from modules.llm.Gemini import Gemini
        return Gemini("gemini-1.5-flash")
    elif model_name.startswith("deepseek"):
        from modules.llm.DeepSeek import DeepSeek
        return DeepSeek()
    else:
        print(f'Warning! undefined model {model_name}, use gpt-4o-mini instead.')
        from modules.llm.LangChainGPT import LangChainGPT
        return LangChainGPT()

def load_config(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        args = json.load(file)
    return args

def save_config(args,filepath):
    with open(filepath, "w", encoding ="utf8") as json_file:
        json.dump(args,json_file,indent = 1,ensure_ascii = False)
    return

def smart_path(path):
    file_dir = osp.dirname(osp.abspath(__file__))
    if osp.isabs(path):
        return path
    else:
        return osp.join(file_dir,path)
args = load_config(smart_path("./config.json"))

# Baidu preparation
endpoint = "http://api.fanyi.baidu.com"
path = "/api/trans/vip/translate"
url = endpoint + path
headers = {"Content-Type": "application/x-www-form-urlencoded"}
# Generate salt and sign
def make_md5(s, encoding="utf-8"):
    return md5(s.encode(encoding)).hexdigest()

def get_baidu_completion(text,api_id,api_key,from_lang,to_lang):
    salt = random.randint(32768, 65536)
    sign = make_md5(api_id + text + str(salt) + api_key)
    payload = {"appid": api_id, "q": text, "from": from_lang, "to": to_lang, "salt": salt, "sign": sign}
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()
    return result["trans_result"][0]["dst"]

# OPENAI preparation
openai_api_key = args["openai_api_settings"]["openai_api_key"]
time_limit = float(args["openai_api_settings"]["time_limit"])
client = openai.OpenAI(api_key = openai_api_key)

class GPTThread(threading.Thread):
    def __init__(self, model, messages, temperature):
        super().__init__()
        self.model = model
        self.messages = messages
        self.temperature = temperature
        self.result = ""
    def terminate(self):
        self._running = False 
    def run(self):
        response = client.chat.completions.create(
        model=self.model,
        messages=self.messages,
        temperature=self.temperature, 
    )
        self.result = response.choices[0].message.content
    
def get_gpt_completion(prompt, time_limit = 10, model="gpt-40-mini"):
    messages = [{"role": "user", "content": prompt}]
    temperature = random.uniform(0,1)
    thread = GPTThread(model, messages,temperature)
    thread.start()
    thread.join(time_limit)
    if thread.is_alive():
        thread.terminate()
        print("请求超时")
        return "TimeoutError", False
    else:
        return thread.result, True
    
class LLMThread(threading.Thread):
    def __init__(self, llm, prompt, temperature):
        super().__init__()
        self.llm = llm
        self.prompt = prompt
        self.temperature = temperature
        self.result = ""
    def terminate(self):
        self._running = False 
    def run(self):
        self.result = self.llm.chat(self.prompt, temperature = self.temperature)
    
def get_llm_completion(prompt, time_limit = 10, model_name="gpt-4o-mini"):
    llm = get_models(model_name)
    temperature = 0.7
    thread = LLMThread(llm, prompt,temperature)
    thread.start()
    thread.join(time_limit)
    if thread.is_alive():
        thread.terminate()
        print("请求超时")
        return "TimeoutError", False
    else:
        return thread.result, True
    
def left_pad_zero(number, digit):
    number_str = str(number)
    padding_count = digit - len(number_str)
    padded_number_str = "0" * padding_count + number_str
    return padded_number_str

def generate_ids(num: int):
    length = len(str(num))+1
    ids = []
    for i in range(num):
        ids.append(left_pad_zero(i,length))
    return ids

def convert_to_json(files, text_col, name_col, id_col):
    out_files = []
    for file_target in files:
        dic = {}
        path = file_target.name
        dir = osp.dirname(path)
        base_name = osp.basename(path)
        new_name = base_name[:-4]+".json"
        new_path = osp.join(dir,new_name)
        with open(path,"r",encoding="utf-8") as f:
            reader = csv.DictReader(f)
            line_num = sum(1 for _ in open(path,"r",encoding="utf-8"))
            fieldnames = reader.fieldnames if reader.fieldnames else []
            if id_col not in fieldnames:
                ids = generate_ids(line_num)
                i = 0
                for row in reader:
                    dic[ids[i]]={"name":row[name_col],"text":row[text_col]}
                    for field in fieldnames:
                        if field not in (name_col,text_col):
                            dic[ids[i]][field] = row[field]
                    i += 1
            else:
                for row in reader:
                    dic[row[id_col]]={"name":row[name_col],"text":row[text_col]}
                    for field in fieldnames:
                        if field not in (name_col,text_col,id_col):
                            dic[row[id_col]][field] = row[field]
                
            f.close()
        with open(new_path, "w", encoding= "utf-8") as f2:
            json.dump(dic,f2,indent=1,ensure_ascii=False)
        out_files.append(new_path)
    return out_files

def convert_to_csv(files):
    out_files = []
    for file_target in files:
        path = file_target.name
        dir = osp.dirname(path)
        base_name = osp.basename(path)
        new_name = base_name[:-4]+".csv"
        new_path = osp.join(dir,new_name)
        with open(path, "r", encoding= "utf-8") as f:
            dic = json.load(f)
        field_names = [] 
        for value in dic.values():
            for field in value.keys():
                if field not in field_names: field_names.append(field)
        for key in dic.keys():
            dic[key]["id"] = key
            for field in field_names:
                if field not in dic[key]:
                    dic[key][field] = ""
        field_names.insert(0,"id")
        with open(new_path, "w", encoding= "utf-8",newline="") as f2:
            writer = csv.DictWriter(f2,fieldnames=field_names)
            writer.writeheader()
            writer.writerows(list(dic.values()))
        out_files.append(new_path)
    return out_files

