import openai
import gradio as gr
from utils import *
from os import path as osp
import json
from tqdm import tqdm

# Initialization
config_path = './config.json'
args = load_config(config_path)
path = args['file_path']
print(path)
replace_dict_path = args['replace_dict_path']
name_dict_path = args['name_dict_path']

with open(path, 'r', encoding ='utf8') as json_file:
    dic = json.load(json_file)
id_lis = list(dic.keys())
id_idx = 0
if args['last_edited_id'] in id_lis:
    id_idx = id_lis.index(args['last_edited_id'])


# Dict for replacement
replace_dic = {}
if osp.exists(replace_dict_path):
    with open(replace_dict_path, "r", encoding="utf-8") as f:
        for line in f:
            item = line.split(' ')
            item[1] = item[1].replace('\n','')
            replace_dic[item[0]]=item[1]
        f.close()

# Dict for name
name_dic = {}
if osp.exists(name_dict_path):
    with open(name_dict_path, "r", encoding="gbk") as f:
            for line in f:
                item = line.split(' ')
                item[1] = item[1].replace('\n','')
                name_dic[item[0]]=item[1]

# Translate 
def gpt_translate(text,text_id):
    text = text.replace('\n',' ')
    prompt = f"""翻译为中文:{text}"""
    try:
        translation = get_gpt_completion(prompt, api_key = args['openai_api_settings']['openai_api_key'])
        dic[text_id]['gpt3'] = translation
    except Exception as e:
        print("Exception:", e)
        translation = f'Error:{e}'
    return translation

def baidu_translate(text,text_id):
    text = text.replace('\n',' ')
    try:
        translation = get_baidu_completion(text,api_id = args['baidu_api_settings']['api_id'], api_key = args['baidu_api_settings']['api_key'])
        dic[text_id]['baidu'] = translation
    except Exception as e:
        print("Exception:", e)
        translation = f'Error:{e}'
    return translation

def change_id(text_id):
    global id_idx
    args['last_edited_id'] = text_id
    id_idx = id_lis.index(text_id)
    if 'gpt3' not in dic[text_id]:
        dic[text_id]['gpt3'] = ""
    if 'baidu' not in dic[text_id]:
        dic[text_id]['baidu'] = ""
    if "text_CN" not in dic[text_id]:
        dic[text_id]["text_CN"] = ""
    if dic[text_id]['name'] not in name_dic:
        name_dic[dic[text_id]['name']] = dic[text_id]['name']
    else:
        dic[text_id]['name_CN'] = name_dic[dic[text_id]['name']]
    with open(config_path, 'w', encoding ='utf8') as json_file:
        json.dump(args,json_file,indent = 1,ensure_ascii = False)
    return dic[text_id]['text'],dic[text_id]['name'],name_dic[dic[text_id]['name']],dic[text_id]['gpt3'],dic[text_id]["baidu"],dic[text_id]["text_CN"]

def last_text():
    global id_idx
    if id_idx > 0:
        id_idx -= 1
    return id_lis[id_idx]

def next_text():
    global id_idx
    if id_idx < len(id_lis)-1:
        id_idx += 1
    return id_lis[id_idx]

def replace(text_gpt,text_baidu,text_final,text_id):
    if not text_id:
        text_id = id_lis[id_idx]
    if osp.exists(replace_dict_path):
        with open(replace_dict_path, "r", encoding="utf-8") as f:
            for line in f:
                item = line.split(' ')
                item[1] = item[1].replace('\n','')
                replace_dic[item[0]]=item[1]
            f.close()
    for key,value in replace_dic.items():
        text_gpt = text_gpt.replace(key, value)
        text_baidu = text_baidu.replace(key, value)
        text_final = text_final.replace(key, value)
    dic[text_id]['gpt3'] = text_gpt
    dic[text_id]['baidu'] = text_baidu
    dic[text_id]["text_CN"] = text_final
    return text_gpt,text_baidu,text_final

def change_final(text,text_id):
    dic[text_id]["text_CN"] = text
    return id_lis[id_idx]

def change_name(name,name_cn,text_id):
    name_dic[name] = name_cn
    dic[text_id]['name_CN'] = name_cn
    return id_lis[id_idx]

# Save
def save_json():
    with open(path, 'w', encoding ='utf8') as json_file:
        json.dump(dic,json_file,indent = 1,ensure_ascii = False)
    if osp.exists(name_dict_path):
        with open(name_dict_path,'w') as f:
            for key,value in name_dic.items():
                f.write(f"{key} {value}\n")
    return

def upload_json(file_json):
    return
    
def load_last_position():
    return id_lis[id_idx]

def submit_api(baidu_api_id, baidu_api_key,openai_api_key):
    global args
    if baidu_api_id != '':
        args['baidu_api_settings']['api_id'] = baidu_api_id
    if baidu_api_key != '':
        args['baidu_api_settings']['api_key'] = baidu_api_key
    if openai_api_key != '':
        args['openai_api_settings']['openai_api_key'] = openai_api_key
    with open(config_path, 'w', encoding ='utf8') as json_file:
        json.dump(args,json_file,indent = 1,ensure_ascii = False)
    return baidu_api_id, baidu_api_key,openai_api_key
        
# Derive text
def derive_text(radio_type, text_start_id, text_end_id,text_seperator_long,text_seperator_short, output_txt_path):
    if text_start_id not in id_lis or text_end_id not in id_lis or id_lis.index(text_start_id) > id_lis.index(text_end_id):
        return
    start = id_lis.index(text_start_id)
    end = id_lis.index(text_end_id) + 1
    lis = id_lis[start:end]
    if radio_type == '双语|人名文本':
        
        with open(output_txt_path,'w',encoding="utf-8") as f:
            for key in tqdm(lis):
                if key in dic:
                    f.write(text_seperator_long+'\n')
                    f.write(dic[key]['name']+'\n')
                    f.write('\n')
                    f.write(dic[key]['text']+'\n')
                    f.write('\n')
                    f.write(text_seperator_short+'\n')
                
                    f.write(dic[key]['name_CN']+'\n\n')
                    
                    f.write(dic[key]['text_CN']+'\n')
                    f.write('\n')
        return
    if radio_type == '中文|人名文本':
        with open(output_txt_path,'w',encoding="utf-8") as f:
            for key in tqdm(lis):
                if key in dic:
                    f.write(text_seperator_long+'\n')            
                    f.write(dic[key]['name_CN']+'\n\n')
                    
                    f.write(dic[key]['text_CN']+'\n')
                    f.write('\n')
        return        
    if radio_type == '中文|纯文本':
        with open(output_txt_path,'w',encoding="utf-8") as f:
            for key in tqdm(lis):
                if key in dic:
                    f.write(dic[key]['text_CN']+'\n')
                    f.write('\n')

with gr.Blocks() as demo:
    with gr.Tab('编辑页'):
        
        gr.Markdown('## 文本编辑及保存区')
        with gr.Row():
            text_id = gr.Textbox(label = '文本编号')
            button_load = gr.Button('Load last edited position')
        with gr.Row():
            with gr.Column():
                text_name = gr.Textbox(label = 'Name')
                
                text_input = gr.Textbox(label = 'Text', lines=10)
                
            with gr.Column():
                text_name_cn = gr.Textbox(label = 'Name_CN')
                with gr.Row():
                    text_gpt = gr.Textbox(label = 'GPT', lines=3,show_copy_button=True,interactive = True)
                    button_translate_gpt = gr.Button("Translate(GPT)")
                with gr.Row():
                    text_baidu = gr.Textbox(label = 'Baidu', lines=3,show_copy_button=True,interactive = True)
                    
                    button_translate_baidu = gr.Button("Translate(Baidu)")
                text_final = gr.Textbox(label = "Text_CN", lines=3,show_copy_button=True,interactive = True)
                with gr.Row():
                    button_up = gr.Button('↑')
                    button_down = gr.Button('↓')
                    
                    button_replace = gr.Button("Replace")
                    
        with gr.Row():
            button_save = gr.Button("Save JSON")
        
        
        gr.Markdown('## 文档导出区')
        radio_type = gr.Radio(choices = ["中文|纯文本", "中文|人名文本", "双语|人名文本"],label = '导出类型')
        with gr.Row():
            text_start_id = gr.Textbox(label = '起始句id')
            text_end_id = gr.Textbox(label = '结束句id')
        with gr.Row():
            text_seperator_long = gr.Textbox(label = '句间分隔符(长)', value = args['seperator_long'])
            text_seperator_short = gr.Textbox(label = '双语间分隔符(短)', value = args['seperator_short'])
        text_output_path = gr.Textbox(label = '输出文件路径', value = args['output_txt_path'])
        button_derive_text = gr.Button("导出文本")
        
        
    with gr.Tab('文件上传（未启用）'):
        with gr.Row():
            file_json = gr.File(file_count='single',file_types=['json'])
            
    with gr.Tab('API Settings'):
        gr.Markdown('## 百度 API')
        text_baidu_api_id = gr.Textbox(label='Baidu API Id',value = args['baidu_api_settings']['api_id'])
        text_baidu_api_key = gr.Textbox(label='Baidu API Key', value = args['baidu_api_settings']['api_key'])
        gr.Markdown('## OPENAI API')
        text_openai_api = gr.Textbox(label='OPENAI API Key',value = args['openai_api_settings']['openai_api_key'])
        button_api_submit = gr.Button('Submit')
    
    file_json.upload(upload_json, inputs=file_json)
    
    # 文本框行为
    text_id.change(change_id,text_id,[text_input,text_name,text_name_cn,text_gpt,text_baidu,text_final])
    text_final.change(change_final,inputs = [text_final,text_id])
    text_name_cn.change(change_name,inputs = [text_name,text_name_cn,text_id])
    
    # 按钮行为
    button_load.click(load_last_position,outputs = text_id)
    button_up.click(last_text, outputs = text_id)
    button_down.click(next_text, outputs = text_id)
    button_translate_gpt.click(gpt_translate, inputs=[text_input,text_id], outputs=text_gpt)
    button_translate_baidu.click(baidu_translate, inputs=[text_input,text_id], outputs=text_baidu)
    button_replace.click(replace, inputs = [text_gpt,text_baidu,text_final,text_id], outputs=[text_gpt,text_baidu,text_final])
    button_api_submit.click(submit_api, inputs = [text_baidu_api_id,text_baidu_api_key,text_openai_api],outputs=[text_baidu_api_id,text_baidu_api_key,text_openai_api])
    button_save.click(save_json)
    button_derive_text.click(derive_text,
                             inputs = [radio_type, text_start_id, text_end_id,
                                       text_seperator_long,text_seperator_short,text_output_path])
demo.launch()

