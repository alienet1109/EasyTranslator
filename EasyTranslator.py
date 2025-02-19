import gradio as gr
import os
from os import path as osp
import json
from utils import *
from themes import *

# Initialization
# id指代台词的编号，为一个字符串
# idx指代顺序排列的序号，0,1,2,...
config_path = osp.join(osp.dirname(osp.abspath(__file__)),"./config.json")
args = load_config(config_path)

model_list = list(MODEL_NAME_DICT.keys()) + ["gpt3","baidu"]
for key, value in args["API_KEYS"].items():
    if "API_KEY" in key and "YOUR" not in value:
        os.environ[key] = value

if_save_id_immediately = True if int(args["if_save_id_immediately"]) else False
moyu_mode = True if int(args["moyu_mode"]) else False
path = args["file_path"]
abs_path = smart_path(path)
replace_dict_path = smart_path(args["replace_dict_path"])
name_dict_path = smart_path(args["name_dict_path"])
altered_text_finals= set()
time_limit = int(args["time_limit"]) if "time_limit" in args and isinstance(args["time_limit"],int) else 10

if osp.exists(abs_path):
    with open(abs_path, "r", encoding ="utf8") as json_file:
        dic = json.load(json_file)
    id_lis = list(dic.keys())
    idx_dic = dict()
    for idx,id_ in enumerate(id_lis):
        idx_dic[id_] = idx 
    id_idx = 0
    if args["last_edited_id"] in id_lis:
        id_idx = idx_dic[args["last_edited_id"]]

# Dict for replacement
replace_dic = {}
if osp.exists(replace_dict_path):
    with open(replace_dict_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line:continue
            item = line.split(" ")
            item[1] = item[1].replace("\n","")
            replace_dic[item[0]]=item[1]
        f.close()

# Dict for name
name_dic = {}
if osp.exists(name_dict_path):
    with open(name_dict_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line:continue
                item = line.split(" ")
                item[1] = item[1].replace("\n","")
                name_dic[item[0]]=item[1]

# Translate 
def llm_translate(text, text_id, model_name):
    if model_name not in model_list:
        return ""
    if model_name == "baidu":
        return baidu_translate(text,text_id)
    elif model_name == "gpt3":
        return gpt_translate(text,text_id)
    text = text.replace("\n"," ")
    prompt = args["openai_api_settings"]["prompt_prefix"]+text+args["openai_api_settings"]["prompt_postfix"]
    translation, if_succ = get_llm_completion(prompt, time_limit=int(time_limit), model_name=model_name)
    if dic[text_id]["text"].replace("\n"," ") == text and if_succ:
        dic[text_id][model_name] = translation  
    save_config(args,config_path)  
    return translation

def gpt_translate(text,text_id):
    text = text.replace("\n"," ")
    prompt = args["openai_api_settings"]["prompt_prefix"]+text+args["openai_api_settings"]["prompt_postfix"]
    translation, if_succ = get_gpt_completion(prompt, time_limit=int(time_limit))
    if dic[text_id]["text"].replace("\n"," ") == text and if_succ:
        dic[text_id]["gpt3"] = translation
    return translation

def baidu_translate(text,text_id):
    text = text.replace("\n"," ")
    translation = get_baidu_completion(text,
                                        api_id = args["baidu_api_settings"]["api_id"],
                                        api_key = args["baidu_api_settings"]["api_key"],
                                        from_lang=args["baidu_api_settings"]["from_lang"],
                                        to_lang=args["baidu_api_settings"]["to_lang"],)
    if dic[text_id]["text"].replace("\n"," ") == text:
        dic[text_id]["baidu"] = translation
    return translation

def batch_translate(dropdown_batch_model, check, text_start_id,text_end_id,progress=gr.Progress()):
    progress(0, desc="Starting...")
    if text_start_id not in id_lis or text_end_id not in id_lis or idx_dic[text_start_id] > idx_dic[text_end_id]:
        gr.Warning("找不到指定序号, 或id前后顺序错误")
        return
    start = idx_dic[text_start_id]
    end = idx_dic[text_end_id] + 1
    lis = id_lis[start:end]
    for key in progress.tqdm(lis):
        llm_translate(dic[key]['text'],key,dropdown_batch_model)
        time.sleep(0.05)
    if check:        
        save_json(show_info=False)
    gr.Info(f"批量机翻成功, 共完成{end-start}句翻译")
    return f"已完成{end-start}句翻译"
    
# Other actions
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

def replace(dropbox_model1,dropbox_model2,text_model1,text_model2,text_final,text_id, check_file = True):
    if not text_id:
        text_id = id_lis[id_idx]
    if check_file:
        if osp.exists(replace_dict_path):
            with open(replace_dict_path, "r", encoding="utf-8") as f:
                for line in f:
                    item = line.split(" ")
                    item[1] = item[1].replace("\n","")
                    replace_dic[item[0]]=item[1]
                f.close()
    for key,value in replace_dic.items():
        text_model1 = text_model1.replace(key, value)
        text_model2 = text_model2.replace(key, value)
        text_final = text_final.replace(key, value)
    dic[text_id][dropbox_model1] = text_model1
    dic[text_id][dropbox_model2] = text_model2
    dic[text_id]["text_CN"] = text_final
    return text_model1,text_model2,text_final

def change_model_name0(text_id, model_name):
    # 改变机翻文本框
    if not text_id or not text_id in idx_dic: return ""
    if model_name not in model_list: return ""
    args["selected_model"][0] = model_name
    if model_name in dic[text_id]:
        return dic[text_id][model_name]
    else:
        return ""
def change_model_name1(text_id, model_name):
    # 改变机翻文本框
    if not text_id or not text_id in idx_dic: return ""
    if model_name not in model_list: return ""
    args["selected_model"][1] = model_name
    if model_name in dic[text_id]:
        return dic[text_id][model_name]
    else:
        return ""

def change_id(text_id, dropbox_model1, dropbox_model2):
    if not text_id or text_id not in idx_dic: return args["file_path"],"","","","","",""
    global id_idx
    id_idx = idx_dic[text_id]
    if dropbox_model1 not in dic[text_id]:
        dic[text_id][dropbox_model1] = ""
    if dropbox_model2 not in dic[text_id]:
        dic[text_id][dropbox_model2] = ""
    if "text_CN" not in dic[text_id]:
        dic[text_id]["text_CN"] = ""
    if dic[text_id]["name"] not in name_dic:
        name_dic[dic[text_id]["name"]] = dic[text_id]["name"]
    dic[text_id]["name_CN"] = name_dic[dic[text_id]["name"]]
    replace(dropbox_model1, dropbox_model2, dic[text_id][dropbox_model1],dic[text_id][dropbox_model2],dic[text_id]["text_CN"],text_id,False)
    args["selected_model"] = [dropbox_model1, dropbox_model2]
    if if_save_id_immediately:
        args["last_edited_id"] = text_id
        save_config(args,config_path)
    return args["file_path"],dic[text_id]["text"],dic[text_id]["name"],name_dic[dic[text_id]["name"]],\
        dic[text_id][dropbox_model1],dic[text_id][dropbox_model2],dic[text_id]["text_CN"]
        
def change_final(text,text_id):
    if not text_id or not text_id in idx_dic: return
    if text != dic[text_id]["text_CN"]:
        dic[text_id]["text_CN"] = text
        altered_text_finals.add(text_id)
    return 

def change_name(name,name_cn,text_id):
    if not text_id or not text_id in idx_dic: return
    name_dic[name] = name_cn
    dic[text_id]["name_CN"] = name_cn
    return 

def change_apikey(dropdown_apikey):
    return args["API_KEYS"][dropdown_apikey] if dropdown_apikey in args["API_KEYS"] else ""
    
def save_json(show_info = True):
    global altered_text_finals
    with open(abs_path, "w", encoding ="utf8") as json_file:
        json.dump(dic,json_file,indent = 1,ensure_ascii = False)
    if osp.exists(name_dict_path):
        with open(name_dict_path,"w",encoding = "utf-8") as f:
            for key,value in name_dic.items():
                f.write(f"{key} {value}\n")
    if show_info:
        gr.Info(f"JSON保存成功, 共更新{len(altered_text_finals)}句译文")
    altered_text_finals = set()

def save_last_position(text_id):
    args["last_edited_id"] = text_id
    save_config(args,config_path)
    return

def load_last_position(text_path):
    global id_idx,id_lis,idx_dic,path,dic
    if not osp.exists(smart_path(text_path)):
        raise gr.Error("文件不存在")
    if path != text_path:
        path = text_path
        with open(smart_path(text_path), "r", encoding ="utf8") as json_file:
            dic = json.load(json_file)
        id_lis = list(dic.keys())
        idx_dic = dict()
        for idx,id_ in enumerate(id_lis):
            idx_dic[id_] = idx 
        id_idx = 0
        args["file_path"] = path
        save_config(args,config_path)
    return args["last_edited_id"]

def submit_api(baidu_api_id, baidu_api_key, from_lang, to_lang, dropdown_apikey,text_apikey,prefix,postfix,target_id):
    global args
    if baidu_api_id != "":
        args["baidu_api_settings"]["api_id"] = baidu_api_id
    if baidu_api_key != "":
        args["baidu_api_settings"]["api_key"] = baidu_api_key
    if from_lang != "":
        args["baidu_api_settings"]["from_lang"] = from_lang
    if to_lang != "":
        args["baidu_api_settings"]["to_lang"] = to_lang
    if text_apikey != "":
        args["API_KEYS"][dropdown_apikey] = text_apikey
    args["openai_api_settings"]["prompt_prefix"] = prefix
    args["openai_api_settings"]["prompt_postfix"] = postfix
    args["target_id"] = target_id
    save_config(args,config_path)
    return 

def refresh_context(refresh_id,length,context_type):
    if not refresh_id or not refresh_id in idx_dic: return [],id_lis[id_idx]
    length = int(length)
    idx = idx_dic[refresh_id]
    if context_type == "上下文":
        ids = id_lis[max(idx-length, 0):idx+length+1]
    elif context_type == "上文":
        ids = id_lis[max(idx-length, 0):idx+1]
    elif context_type == "下文":
        ids = id_lis[idx:idx+length+1]
    data = []
    for i in ids:
        if dic[i]["name"] not in name_dic:
            name_dic[dic[i]["name"]] = dic[i]["name"]
        dic[i]["name_CN"] = name_dic[dic[i]["name"]]
        if 'text_CN' not in dic[i]:
            dic[i]['text_CN'] = ""
        row = [i, dic[i]['name'],dic[i]['name_CN'], dic[i]['text'],dic[i]['text_CN']]
        if i == id_lis[idx]: row[0] = f"**{i}**"
        if i in altered_text_finals:
            row[4] = f"*{row[4]}"
        data.append(row)
    return data,id_lis[id_idx]

def save_context(data, refresh_id, if_save = False):
    altered = 0
    for i in range(len(data)):
        text_id = data['id'][i]
        text_cn = data['text_CN'][i]
        text_id = text_id.replace("*","")
        if text_id in altered_text_finals and text_cn and text_cn[0] == "*":
            text_cn = text_cn[1:]
        if dic[text_id]['text_CN'] != text_cn:
            altered += 1
            altered_text_finals.add(text_id)
            dic[text_id]['text_CN'] = text_cn
    gr.Info(f"已修改{altered}条译文")
    if if_save:
        save_json()
    return

# Derive text
def derive_text(radio_type, text_start_id, text_end_id,text_seperator_long,text_seperator_short, output_txt_path):
    output_txt_path = smart_path(output_txt_path)
    if output_txt_path[-4:] != ".txt":
        gr.Warning("输出路径错误")
        return
    if text_start_id not in id_lis or text_end_id not in id_lis or idx_dic[text_start_id] > idx_dic[text_end_id]:
        gr.Warning("找不到指定序号, 或id前后顺序错误")
        return
    start = idx_dic[text_start_id]
    end = idx_dic[text_end_id] + 1
    lis = id_lis[start:end]
    if radio_type == "双语|人名文本":
        with open(output_txt_path,"w",encoding="utf-8") as f:
            for key in lis:
                # if key[-3:] == "001":
                #     f.write("【"+key[-4]+"】\n")
                f.write(text_seperator_long+"\n")
                f.write(dic[key]["name"]+"\n")
                f.write("\n")
                f.write(dic[key]["text"]+"\n")
                f.write("\n")
                f.write(text_seperator_short+"\n")
                f.write(dic[key]["name_CN"]+"\n\n")
                f.write(dic[key]["text_CN"]+"\n")
                f.write("\n")
        return
    if radio_type == "中文|人名文本":
        with open(output_txt_path,"w",encoding="utf-8") as f:
            for key in lis:
                # if key[-3:] == "001":
                #     f.write("【"+key[-4]+"】\n")
                f.write(text_seperator_long+"\n")            
                f.write(dic[key]["name_CN"]+"\n\n")
                f.write(dic[key]["text_CN"]+"\n")
                f.write("\n")
        return        
    if radio_type == "中文|单次人名文本":
        with open(output_txt_path,"w",encoding="utf-8") as f:
            name_lis = []
            for key in lis:
                name = dic[key]["name_CN"]
                if name not in name_lis:
                    name_lis.append(name)
                    f.write(name + ": "+ dic[key]["text_CN"]+"\n")
                else:
                    f.write(dic[key]["text_CN"]+"\n")
                f.write("\n")
    if radio_type == "中文|纯文本":
        with open(output_txt_path,"w",encoding="utf-8") as f:
            for key in lis:
                f.write(dic[key]["text_CN"]+"\n")
                f.write("\n")
    gr.Info(f"Txt导出成功, 共导出{len(lis)}条记录")

def get_remaining_text_num():
    if args["target_id"] in id_lis:
        target_idx= idx_dic[args["target_id"]]
        rem = target_idx - id_idx
        label = f"目标剩余{rem}条"
    else:
        label = "目标剩余???条"
    return label

def merge_json(merged_path,file_merging_json,text_start_id,text_end_id,type):
    merged_path = smart_path(merged_path)
    if not osp.exists(merged_path):
        gr.Warning("路径不存在")
        return
    with open(merged_path, "r", encoding ="utf8") as json_file:
        dic_merge = json.load(json_file)
    id_lis_merge = list(dic_merge.keys())
    idx_dic_merge = dict()
    for idx,id_ in enumerate(id_lis_merge):
        idx_dic_merge[id_] = idx 
    if text_start_id not in id_lis_merge or text_end_id not in id_lis_merge or idx_dic_merge[text_start_id] > idx_dic_merge[text_end_id]:
        gr.Warning("找不到指定序号, 或id前后顺序错误")
        return
    path = file_merging_json.name
    with open(path, "r", encoding ="utf8") as json_file:
        dic_new = json.load(json_file)
    for idx in range(idx_dic_merge[text_start_id],idx_dic_merge[text_end_id] + 1):
        if type == "仅人工翻译":
            dic_merge[id_lis_merge[idx]]['text_CN'] = dic_new[id_lis_merge[idx]]['text_CN']
        else:
            dic_merge[id_lis_merge[idx]] = dic_new[id_lis_merge[idx]]
    with open(merged_path, "w", encoding ="utf8") as json_file:
        json.dump(dic_merge,json_file,indent = 1,ensure_ascii = False)
    gr.Info(f"合并成功，共更新{idx_dic_merge[text_end_id] - idx_dic_merge[text_start_id] + 1}条译文")
    return
        
def output_json(merged_path,text_start_id,text_end_id):
    merged_path = smart_path(merged_path)
    if not osp.exists(merged_path):
        gr.Warning("路径不存在")
        return
    with open(merged_path, "r", encoding ="utf8") as json_file:
        dic_merge = json.load(json_file)
    id_lis_merge = list(dic_merge.keys())
    idx_dic_merge = dict()
    for idx,id_ in enumerate(id_lis_merge):
        idx_dic_merge[id_] = idx 
    if text_start_id not in id_lis_merge or text_end_id not in id_lis_merge or idx_dic_merge[text_start_id] > idx_dic_merge[text_end_id]:
        gr.Warning("找不到指定序号, 或id前后顺序错误")
        return
    dic_new = {}
    for idx in range(idx_dic_merge[text_start_id],idx_dic_merge[text_end_id] + 1):
        dic_new[id_lis_merge[idx]] = dic_merge[id_lis_merge[idx]]
    name = "small_" + osp.basename(path)
    new_path = osp.join(osp.dirname(merged_path), name)
    with open(new_path, "w", encoding ="utf8") as json_file:
        json.dump(dic_new,json_file,indent = 1,ensure_ascii = False)
    return new_path
  
shortcut_js = """
<script>
function shortcuts(e) {

    if (e.key.toLowerCase() == "s" && e.altKey) {
        document.getElementById("button_save").click();
    }
    if (e.key.toLowerCase() == "w" && e.altKey) {
        document.getElementById("button_up").click();
    }
    if (e.key.toLowerCase() == "x" && e.altKey) {
        document.getElementById("button_down").click();
    }
    if (e.key.toLowerCase() == "r" && e.altKey) {
        document.getElementById("button_replace").click();
    }
    if (e.key.toLowerCase() == "q" && e.altKey) {
        document.getElementById("button_translate_model1").click();
    }
    if (e.key.toLowerCase() == "e" && e.altKey) {
        document.getElementById("button_translate_model2").click();
    }
    
}
document.addEventListener('keyup', shortcuts, false);
</script>
"""

with gr.Blocks(theme=Theme1(),head=shortcut_js) as demo:
    gr.Markdown("# <center>EasyTranslator v1.1.0</center> ",visible=True)
    # 文本编辑页
    with gr.Tab("文本编辑"):
        gr.Markdown("## 文本编辑及保存区")
        with gr.Row():
            text_file_path = gr.Textbox(label = "File Path - 数据文件JSON路径", value = args["file_path"])
            text_id = gr.Textbox(label = "Text id - 当前文本id",show_copy_button=True)
            button_load_pos = gr.Button("LOAD last edited position")
            if not if_save_id_immediately:
                button_save_pos = gr.Button("SAVE last edited position")
        with gr.Row():
            if not moyu_mode:
                # 全屏mode
                with gr.Column():
                    text_name = gr.Textbox(label = "Name - 原文人名")
                    text_text = gr.Textbox(label = "Text - 原文文本", lines=10,show_copy_button=True)
                    button_save = gr.Button("SAVE JSON FILE",scale= 2,elem_id = "button_save")
                    dropdown_model1 = gr.Dropdown(choices=model_list,value=args["selected_model"][0], label = "Choose Model1 - 选择模型1",interactive=True)
                    dropdown_model2 = gr.Dropdown(choices=model_list,value=args["selected_model"][1], label = "Choose Model2 - 选择模型2",interactive=True)
                    
                with gr.Column():
                    text_name_cn = gr.Textbox(label = "Name_CN - 译文人名")
                    with gr.Row():
                        text_model1 = gr.Textbox(label="Model1 - 模型1译文",lines=3,show_copy_button=True,interactive = True)
                        button_translate_model1 = gr.Button("Translate(Model1)",elem_id = "button_translate_model1")
                    with gr.Row():
                        text_model2 = gr.Textbox(label="Model2 - 模型2译文",lines=3,show_copy_button=True,interactive = True)
                        button_translate_model2 = gr.Button("Translate(Model2)",elem_id = "button_translate_model2")
                    text_final = gr.Textbox(label = "Text_CN - 人工译文", lines=3,show_copy_button=True,interactive = True)
                    with gr.Row():
                        button_up = gr.Button("↑",elem_id = "button_up")
                        button_down = gr.Button("↓",elem_id = "button_down")
                        button_replace = gr.Button("Replace",elem_id = "button_replace")
            else:
                # 摸鱼mode
                with gr.Column():
                    text_name = gr.Textbox(label = "Name - 原文人名")
                    text_name_cn = gr.Textbox(label = "Name_CN - 译文人名")
                    dropdown_model1 = gr.Dropdown(choices=model_list,value=args["selected_model"][0], label = "Choose Model1 - 选择模型1",interactive=True)
                    dropdown_model2 = gr.Dropdown(choices=model_list,value=args["selected_model"][1], label = "Choose Model2 - 选择模型2",interactive=True)
                with gr.Column():
                    with gr.Row():
                        text_model1 = gr.Textbox(label="Model1 - 模型1译文",lines=3,show_copy_button=True,interactive = True)
                        button_translate_model1 = gr.Button("Translate(Model1)",elem_id = "button_translate_model1")
                    with gr.Row():
                        text_model2 = gr.Textbox(label="Model2 - 模型2译文",lines=3,show_copy_button=True,interactive = True)
                        button_translate_model2 = gr.Button("Translate(Model2)",elem_id = "button_translate_model2")
                    text_text = gr.Textbox(label = "Text - 原文文本", lines=3,show_copy_button=True)
                    text_final = gr.Textbox(label = "Text_CN - 人工译文", lines=3,show_copy_button=True,interactive = True)
                    with gr.Row():
                        button_up = gr.Button("↑",elem_id = "button_up")
                        button_down = gr.Button("↓",elem_id = "button_down")
                        button_replace = gr.Button("Replace",elem_id = "button_replace")
                    button_save = gr.Button("SAVE JSON FILE",scale= 2,elem_id = "button_save")
                    
        label_remaining_text = gr.Label(label="进度",value = "目标剩余???条")
        gr.Markdown("## 批量机翻区")
        with gr.Row():
            text_translate_start_id = gr.Textbox(label = "起始句id")
            text_translate_end_id = gr.Textbox(label = "结束句id")
        with gr.Row():
            dropdown_model_batch = gr.Dropdown(choices=model_list,value=args["selected_model"][0], label = "批量翻译模型选择",interactive=True)
            label_progress = gr.Label(label = "进度条",value="")
        checkbox_if_save_translation = gr.Checkbox(value= False, label = "翻译完成后直接保存文件")
        button_batch_translate = gr.Button("开始批量翻译")   
            
    tab_context = gr.Tab("文本预览及导出")
    with tab_context:
        gr.Markdown("## 上下文预览区")
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    text_refresh_id = gr.Textbox(label = "Text id - 当前文本id", value = args["last_edited_id"])
                    text_context_length = gr.Textbox(label = "上下文长度", value = args["context_half_length"])
                radio_context_type = gr.Radio(choices = ["上下文","上文", "下文"], label = "预览模式",value="下文")
            with gr.Column():
                with gr.Row():
                    button_refresh = gr.Button("Refresh")
                    button_save_context = gr.Button("Save Changes")
                checkbox_if_save_context = gr.Checkbox(value= False, label = "修改直接存入json文件")
        dataframe_context = gr.DataFrame(headers=['id','name','name_CN','text','text_CN'],
                                         interactive=True) 
        gr.Markdown("## 文档导出区")
        radio_type = gr.Radio(choices = ["中文|纯文本","中文|单次人名文本", "中文|人名文本", "双语|人名文本"],label = "导出类型")
        with gr.Row():
            text_derive_start_id = gr.Textbox(label = "起始句id")
            text_derive_end_id = gr.Textbox(label = "结束句id")
        with gr.Row():
            text_seperator_long = gr.Textbox(label = "句间分隔符(长)", value = args["seperator_long"])
            text_seperator_short = gr.Textbox(label = "双语间分隔符(短)", value = args["seperator_short"])
        text_output_path = gr.Textbox(label = "输出文件路径", value = args["output_txt_path"])
        button_derive_text = gr.Button("导出文本")   
        
    # 文件转换页
    with gr.Tab("文件转换"):
        gr.Markdown("## CSV to JSON(支持批量上传)")
        gr.Markdown("准备好台词csv文件（至少包含正序排列的台词）并将台词列命名为text，如自带角色名则将此列命名为name，如自带id则将此列命名为id。\
            在此处上传csv文件，保存生成的json文件，之后在主界面输入json文件路径即可使用。")
        with gr.Row():
            with gr.Column():
                
                file_target_csv = gr.File(file_types=["csv"],file_count = "multiple", label="Input CSV")
                with gr.Row():
                    text_text_column = gr.Textbox(label="text列名",value = args["csv_column_name"]["text"])
                    text_name_column = gr.Textbox(label="name列名",value = args["csv_column_name"]["name"])
                    text_id_column = gr.Textbox(label="id列名(optional)",value = args["csv_column_name"]["id"],placeholder = "若不指定或找不到指定列，程序会自动编号")
                button_convert2json =  gr.Button("Convert")
            file_result_json = gr.File(file_types=["json"],label="Output JSON",interactive=False)
        gr.Markdown("## JSON to CSV(支持批量上传)")
        with gr.Row():
            with gr.Column():
                file_target_json = gr.File(file_types=[".json"],file_count = "multiple",label="Input JSON")
                button_convert2csv =  gr.Button("Convert")
            file_result_csv = gr.File(file_types=[".csv"],label="Output CSV",interactive=False)
            
    # 文件合并页
    with gr.Tab("文件合并"):
        gr.Markdown("## 合并JSON文件")
        gr.Markdown("将两个json文件中的译文合并，方便多人协作。使用方法为上传部分翻译后的json文件，指定起止id。\
            程序会用【上传文件】中，从起始句id到结束句id的全部内容，覆盖【指定地址】中的json文件从起始句id到结束句id的全部内容。\
                若起止id顺序颠倒或不存在，按钮不会作用。请仔细检查并做好备份！！")
        with gr.Column():
  
            text_merged_path = gr.Textbox(label = "File Path - 被覆盖的文件地址", value = args["file_path"])
            file_merging_json = gr.File(file_types=["json"],file_count = "single", label="File to be merged - 用于覆盖的文件")
            with gr.Row():
                text_merge_start_id = gr.Textbox(label="起始句id",value = "")
                text_merge_end_id  = gr.Textbox(label="结束句id",value = "")
                radio_merge_type = gr.Radio(choices = ["仅人工翻译","全部替换"], label = "合并模式",value="仅人工翻译")
                
                button_merge =  gr.Button("Merge")
            
            # button_output_json =  gr.Button("Merge")
        gr.Markdown("## 导出JSON文件")
        gr.Markdown("支持导出起止id范围的小型json文件，以减少协作时的传输负担。使用上面File Path的指定地址。")
        with gr.Row():
            text_output_start_id = gr.Textbox(label="起始句id",value = "")
            text_output_end_id  = gr.Textbox(label="结束句id",value = "")
            button_output =  gr.Button("Output")
        file_output_json = gr.File(file_types=["json"],label="Output JSON",interactive=False)
        
        

    # API设置页
    with gr.Tab("API Settings"):
        gr.Markdown("## 目标id")
        text_target_id = gr.Textbox(label="Target Id",value = args["target_id"])
        gr.Markdown("## API KEY")
        dropdown_apikey = gr.Dropdown(list(args["API_KEYS"].keys()), value="OPENAI_API_KEY",label = "填写API KEY",interactive=True)
        text_apikey = gr.Textbox(label="API KEY",value = args["API_KEYS"]["OPENAI_API_KEY"])
        with gr.Row():
            text_prefix = gr.Textbox(label="Prompt Prefix",value = args["openai_api_settings"]["prompt_prefix"])
            text_postfix = gr.Textbox(label="Prompt Postfix",value = args["openai_api_settings"]["prompt_postfix"])
        gr.Markdown("## 百度 API")
        text_model2_api_id = gr.Textbox(label="Baidu API Id",value = args["baidu_api_settings"]["api_id"])
        text_model2_api_key = gr.Textbox(label="Baidu API Key", value = args["baidu_api_settings"]["api_key"])
        with gr.Row():
            text_from_lang = gr.Textbox(label="From Lang",value = args["baidu_api_settings"]["from_lang"])
            text_to_lang = gr.Textbox(label="To Lang",value = args["baidu_api_settings"]["to_lang"])
        button_api_submit = gr.Button("Submit")
    
    # 标签页行为
    tab_context.select(refresh_context, inputs=[text_id,text_context_length,radio_context_type],outputs=[dataframe_context,text_refresh_id])
    
    # 下拉选框行为
    dropdown_model1.change(change_model_name0, inputs = [text_id,dropdown_model1], outputs=[text_model1])
    dropdown_model2.change(change_model_name1, inputs = [text_id,dropdown_model2], outputs=[text_model2])
    dropdown_apikey.change(change_apikey, inputs=[dropdown_apikey], outputs=[text_apikey])
    
    # 文本框行为
    text_id.change(change_id, inputs = [text_id,dropdown_model1,dropdown_model2],
                outputs = [text_file_path,text_text,text_name,text_name_cn,text_model1,text_model2,text_final])
    text_id.change(get_remaining_text_num,inputs = None, outputs= [label_remaining_text])
    text_final.change(change_final,inputs = [text_final,text_id])
    text_name_cn.change(change_name,inputs = [text_name,text_name_cn,text_id])
    
    # 按钮行为
    # -文本编辑页
    button_load_pos.click(load_last_position,inputs=text_file_path, outputs = text_id)
    if not if_save_id_immediately:
        button_save_pos.click(save_last_position, inputs = [text_id])
    button_up.click(last_text, outputs = text_id)
    button_down.click(next_text, outputs = text_id)
    button_translate_model1.click(llm_translate, 
                            inputs=[text_text, text_id, dropdown_model1], outputs=text_model1)
    button_translate_model2.click(llm_translate, 
                                inputs=[text_text, text_id, dropdown_model2], outputs=text_model2)
    button_replace.click(replace, 
                        inputs = [dropdown_model1,dropdown_model2,text_model1,text_model2,text_final,text_id], 
                        outputs=[text_model1,text_model2,text_final])
    button_save.click(save_json)
    
    button_batch_translate.click(batch_translate, inputs = [dropdown_model_batch,checkbox_if_save_translation,text_translate_start_id,text_translate_end_id],
                                 outputs = [label_progress])
    
    # -预览及导出页
    # button_refresh.click(save_context, inputs=[dataframe_context, text_refresh_id, checkbox_if_save_context])
    button_refresh.click(refresh_context,inputs=[text_refresh_id,text_context_length,radio_context_type], outputs = [dataframe_context,text_id])
    button_save_context.click(save_context, inputs=[dataframe_context, text_refresh_id, checkbox_if_save_context])
    button_derive_text.click(derive_text,
                            inputs = [radio_type, text_derive_start_id, text_derive_end_id,
                                    text_seperator_long,text_seperator_short,text_output_path])
    
    # -文件转换页
    button_convert2json.click(convert_to_json, 
                        inputs = [file_target_csv, text_text_column, text_name_column, text_id_column], 
                        outputs = file_result_json)
    button_convert2csv.click(convert_to_csv, 
                        inputs = file_target_json, 
                        outputs = file_result_csv)
    
    # -文件合并页
    button_merge.click(merge_json, inputs=[text_merged_path,file_merging_json,text_merge_start_id,text_merge_end_id,radio_merge_type])
    button_output.click(output_json, inputs=[text_merged_path,text_output_start_id,text_output_end_id],outputs=file_output_json)
    
    # -API管理页
    button_api_submit.click(submit_api, 
                            inputs = [text_model2_api_id,text_model2_api_key,text_from_lang,text_to_lang,
                                      dropdown_apikey,text_apikey,text_prefix,text_postfix,text_target_id])

demo.queue()

if __name__=="__main__":
    demo.launch(show_error=True)