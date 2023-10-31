import openai
import os
import requests
import random
import json
from hashlib import md5
from os import path as osp
import csv

def load_config(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        args = json.load(file)
    return args
args = load_config('config.json')

# Baidu preparation
api_id = args['baidu_api_settings']['api_id']
api_key = args['baidu_api_settings']['api_key']
from_lang = args['baidu_api_settings']['from_lang']
to_lang =  args['baidu_api_settings']['to_lang']

endpoint = 'http://api.fanyi.baidu.com'
path = '/api/trans/vip/translate'
url = endpoint + path
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
# Generate salt and sign
def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()

def get_baidu_completion(text,api_id=api_id,api_key=api_key):
    salt = random.randint(32768, 65536)
    sign = make_md5(api_id + text + str(salt) + api_key)
    payload = {'appid': api_id, 'q': text, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()
    return result['trans_result'][0]['dst']



# OPENAI preparation
openai_api_key = args['openai_api_settings']['openai_api_key']
if os.getenv("OPENAI_API_KEY"):
    openai_api_key = os.getenv("OPENAI_API_KEY")
def get_gpt_completion(prompt, model="gpt-3.5-turbo",api_key = openai_api_key):
    openai.api_key  = api_key
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, 
    )
    return response.choices[0].message["content"]

def left_pad_zero(number, digit):
    number_str = str(number)
    padding_count = digit - len(number_str)
    padded_number_str = '0' * padding_count + number_str
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
        new_name = base_name[:-4]+'.json'
        new_path = osp.join(dir,new_name)
        with open(path,'r',encoding="utf-8") as f:
            reader = csv.DictReader(f)
            line_num = sum(1 for _ in open(path,'r',encoding="utf-8"))
            fieldnames = reader.fieldnames
            if id_col not in fieldnames:
                ids = generate_ids(line_num)
                i = 0
                for row in reader:
                    dic[ids[i]]={'name':row[name_col],'text':row[text_col]}
                    for field in fieldnames:
                        if field not in (name_col,text_col):
                            dic[ids[i]][field] = row[field]
                    i += 1
            else:
                for row in reader:
                    dic[row[id_col]]={'name':row[name_col],'text':row[text_col]}
                    for field in fieldnames:
                        if field not in (name_col,text_col,id_col):
                            dic[row[id_col]][field] = row[field]
                
            f.close()
        with open(new_path, 'w', encoding= "utf-8") as f2:
            json.dump(dic,f2,indent=1,ensure_ascii=False)
        out_files.append(new_path)
    return out_files
