import openai
import os
import requests
import random
import json
from hashlib import md5

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
