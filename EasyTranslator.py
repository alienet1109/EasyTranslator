import gradio as gr
from os import path as osp
import json
from utils import *
from themes import *

# Initialization
config_path = osp.join(osp.dirname(osp.abspath(__file__)),"./config.json")
args = load_config(config_path)
if_save_id_immediately = True if int(args["if_save_id_immediately"]) else False
moyu_mode = True if int(args["moyu_mode"]) else False
path = args["file_path"]
abs_path = smart_path(path)
replace_dict_path = smart_path(args["replace_dict_path"])
name_dict_path = smart_path(args["name_dict_path"])
altered_text_finals= set()


if osp.exists(abs_path):
    with open(abs_path, "r", encoding ="utf8") as json_file:
        dic = json.load(json_file)
    id_lis = list(dic.keys())
    id_idx = 0
    if args["last_edited_id"] in id_lis:
        id_idx = id_lis.index(args["last_edited_id"])

# Dict for replacement
replace_dic = {}
if osp.exists(replace_dict_path):
    with open(replace_dict_path, "r", encoding="utf-8") as f:
        for line in f:
            item = line.split(" ")
            item[1] = item[1].replace("\n","")
            replace_dic[item[0]]=item[1]
        f.close()

# Dict for name
name_dic = {}
if osp.exists(name_dict_path):
    with open(name_dict_path, "r", encoding="utf-8") as f:
            for line in f:
                item = line.split(" ")
                item[1] = item[1].replace("\n","")
                name_dic[item[0]]=item[1]

# Translate 
def gpt_translate(text,text_id):
    text = text.replace("\n"," ")
    prompt = args["openai_api_settings"]["prompt_prefix"]+text+args["openai_api_settings"]["prompt_postfix"]
    translation, if_succ = get_gpt_completion(prompt, api_key = args["openai_api_settings"]["openai_api_key"])
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

def batch_translate(radio, check, text_start_id,text_end_id,progress=gr.Progress()):
    progress(0, desc="Starting...")
    if text_start_id not in id_lis or text_end_id not in id_lis or id_lis.index(text_start_id) > id_lis.index(text_end_id):
        gr.Warning("找不到指定序号, 或id前后顺序错误")
        return
    start = id_lis.index(text_start_id)
    end = id_lis.index(text_end_id) + 1
    lis = id_lis[start:end]
    if radio == "Gpt3":
        for key in progress.tqdm(lis):
            gpt_translate(dic[key]['text'],key)
            time.sleep(0.1)
    if radio == 'Baidu':
        for key in progress.tqdm(lis):
            baidu_translate(dic[key]['text'],key)
            time.sleep(0.1)
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

def replace(text_gpt,text_baidu,text_final,text_id, check_file = True):
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
        text_gpt = text_gpt.replace(key, value)
        text_baidu = text_baidu.replace(key, value)
        text_final = text_final.replace(key, value)
    dic[text_id]["gpt3"] = text_gpt
    dic[text_id]["baidu"] = text_baidu
    dic[text_id]["text_CN"] = text_final
    return text_gpt,text_baidu,text_final

def change_id(text_id):
    global id_idx
    id_idx = id_lis.index(text_id)
    if "gpt3" not in dic[text_id]:
        dic[text_id]["gpt3"] = ""
    if "baidu" not in dic[text_id]:
        dic[text_id]["baidu"] = ""
    if "text_CN" not in dic[text_id]:
        dic[text_id]["text_CN"] = ""
    if dic[text_id]["name"] not in name_dic:
        name_dic[dic[text_id]["name"]] = dic[text_id]["name"]
    dic[text_id]["name_CN"] = name_dic[dic[text_id]["name"]]
    replace(dic[text_id]["gpt3"],dic[text_id]["baidu"],dic[text_id]["text_CN"],text_id,False)
    if if_save_id_immediately:
        args["last_edited_id"] = text_id
        save_config(args,config_path)
    return args["file_path"],dic[text_id]["text"],dic[text_id]["name"],name_dic[dic[text_id]["name"]],\
        dic[text_id]["gpt3"],dic[text_id]["baidu"],dic[text_id]["text_CN"]
        
def change_final(text,text_id):
    if text != dic[text_id]["text_CN"]:
        dic[text_id]["text_CN"] = text
        altered_text_finals.add(text_id)
    return id_lis[id_idx]

def change_name(name,name_cn,text_id):
    name_dic[name] = name_cn
    dic[text_id]["name_CN"] = name_cn
    return id_lis[id_idx]

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
    global id_idx,id_lis,path,dic
    if not osp.exists(smart_path(text_path)):
        raise gr.Error("文件不存在")
    if path != text_path:
        path = text_path
        with open(smart_path(text_path), "r", encoding ="utf8") as json_file:
            dic = json.load(json_file)
        id_lis = list(dic.keys())
        id_idx = 0
        args["file_path"] = path
        save_config(args,config_path)
    return args["last_edited_id"]

def submit_api(baidu_api_id, baidu_api_key, from_lang, to_lang, openai_api_key,prefix,postfix):
    global args
    if baidu_api_id != "":
        args["baidu_api_settings"]["api_id"] = baidu_api_id
    if baidu_api_key != "":
        args["baidu_api_settings"]["api_key"] = baidu_api_key
    if from_lang != "":
        args["baidu_api_settings"]["from_lang"] = from_lang
    if to_lang != "":
        args["baidu_api_settings"]["to_lang"] = to_lang
    if openai_api_key != "":
        args["openai_api_settings"]["openai_api_key"] = openai_api_key
    args["openai_api_settings"]["prompt_prefix"] = prefix
    args["openai_api_settings"]["prompt_postfix"] = postfix
    save_config(args,config_path)
    return 

def refresh_context(refresh_id,length,context_type):
    length = int(length)
    idx = id_lis.index(refresh_id)
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
        if text_id == f"**{refresh_id}**":
            text_id = refresh_id
        if text_id in altered_text_finals and text_cn and text_cn[0] == "*":
            text_cn = text_cn[1:]
        if dic[text_id]['text_CN'] != text_cn:
            altered += 1
            altered_text_finals.add(text_id)
            dic[text_id]['text_CN'] = text_cn
    gr.Info(f"已更新{altered}条译文")
    if if_save:
        save_json()
    return

# Derive text
def derive_text(radio_type, text_start_id, text_end_id,text_seperator_long,text_seperator_short, output_txt_path):
    output_txt_path = smart_path(output_txt_path)
    if output_txt_path[-4:] != ".txt":
        gr.Warning("输出路径错误")
        return
    if text_start_id not in id_lis or text_end_id not in id_lis or id_lis.index(text_start_id) > id_lis.index(text_end_id):
        gr.Warning("找不到指定序号, 或id前后顺序错误")
        return
    start = id_lis.index(text_start_id)
    end = id_lis.index(text_end_id) + 1
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
    
with gr.Blocks(theme=Theme1()) as demo:
    gr.Markdown("# <center>EasyTranslatorv1.0.4</center>",visible=True)
    # 文本编辑页
    with gr.Tab("文本编辑"):
        gr.Markdown("## 文本编辑及保存区")
        with gr.Row():
            text_file_path = gr.Textbox(label = "File Path", value = args["file_path"])
            text_id = gr.Textbox(label = "Text id",show_copy_button=True)
            button_load_pos = gr.Button("LOAD last edited position")
            if not if_save_id_immediately:
                button_save_pos = gr.Button("SAVE last edited position")
        with gr.Row():
            if not moyu_mode:
                # 全屏mode
                with gr.Column():
                    text_name = gr.Textbox(label = "Name")
                    text_text = gr.Textbox(label = "Text", lines=10,show_copy_button=True)
                    button_save = gr.Button("SAVE FILE",scale= 2)
                with gr.Column():
                    text_name_cn = gr.Textbox(label = "Name_CN")
                    with gr.Row():
                        text_gpt = gr.Textbox(label = "GPT", lines=3,show_copy_button=True,interactive = True)
                        button_translate_gpt = gr.Button("Translate(GPT)")
                    with gr.Row():
                        text_baidu = gr.Textbox(label = "Baidu", lines=3,show_copy_button=True,interactive = True)    
                        button_translate_baidu = gr.Button("Translate(Baidu)")
                    text_final = gr.Textbox(label = "Text_CN", lines=3,show_copy_button=True,interactive = True)
                    with gr.Row():
                        button_up = gr.Button("↑")
                        button_down = gr.Button("↓")
                        button_replace = gr.Button("Replace")
            else:
                # 摸鱼mode
                with gr.Column():
                    button_save = gr.Button("SAVE FILE",scale= 2)
                    text_name = gr.Textbox(label = "Name")
                    text_name_cn = gr.Textbox(label = "Name_CN")
                with gr.Column():
                    with gr.Row():
                        text_gpt = gr.Textbox(label = "GPT", lines=3,show_copy_button=True,interactive = True)
                        button_translate_gpt = gr.Button("Translate(GPT)")
                    with gr.Row():
                        text_baidu = gr.Textbox(label = "Baidu", lines=3,show_copy_button=True,interactive = True)    
                        button_translate_baidu = gr.Button("Translate(Baidu)")
                    text_text = gr.Textbox(label = "Text", lines=3,show_copy_button=True)
                    text_final = gr.Textbox(label = "Text_CN", lines=3,show_copy_button=True,interactive = True)
                    with gr.Row():
                        button_up = gr.Button("↑")
                        button_down = gr.Button("↓")
                        button_replace = gr.Button("Replace")
        gr.Markdown("## 批量机翻区")
        with gr.Row():
            text_translate_start_id = gr.Textbox(label = "起始句id")
            text_translate_end_id = gr.Textbox(label = "结束句id")
        with gr.Row():
            radio_translator = gr.Radio(choices = ["Baidu","Gpt3"],label = "接口")
            label_progress = gr.Label(label = "进度条",value="")
        checkbox_if_save_translation = gr.Checkbox(value= False, label = "翻译完成后直接保存JSON")
        button_batch_translate = gr.Button("批量翻译")   
            
    tab_context = gr.Tab("文本预览及导出")
    with tab_context:
        gr.Markdown("## 上下文预览区")
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    text_refresh_id = gr.Textbox(label = "编号", value = args["last_edited_id"])
                    text_context_length = gr.Textbox(label = "上下文长度", value = args["context_half_length"])
                radio_context_type = gr.Radio(choices = ["上下文","上文", "下文"], label = "预览模式",value="下文")
            with gr.Column():
                with gr.Row():
                    button_refresh = gr.Button("Refresh")
                    button_save_context = gr.Button("Save Changes")
                checkbox_if_save_context = gr.Checkbox(value= False, label = "修改直接保存JSON")
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
                file_target_json = gr.File(file_types=["json"],file_count = "multiple",label="Input JSON")
                button_convert2csv =  gr.Button("Convert")
            file_result_csv = gr.File(file_types=["jcsv"],label="Output CSV",interactive=False)
    
    # API设置页
    with gr.Tab("API Settings"):
        gr.Markdown("## 百度 API")
        text_baidu_api_id = gr.Textbox(label="Baidu API Id",value = args["baidu_api_settings"]["api_id"])
        text_baidu_api_key = gr.Textbox(label="Baidu API Key", value = args["baidu_api_settings"]["api_key"])
        with gr.Row():
            text_from_lang = gr.Textbox(label="From Lang",value = args["baidu_api_settings"]["from_lang"])
            text_to_lang = gr.Textbox(label="To Lang",value = args["baidu_api_settings"]["to_lang"])
        gr.Markdown("## OPENAI API")
        text_openai_api = gr.Textbox(label="OPENAI API Key",value = args["openai_api_settings"]["openai_api_key"])
        with gr.Row():
            text_prefix = gr.Textbox(label="Prompt Prefix",value = args["openai_api_settings"]["prompt_prefix"])
            text_postfix = gr.Textbox(label="Prompt Postfix",value = args["openai_api_settings"]["prompt_postfix"])
        button_api_submit = gr.Button("Submit")
    
    
    # 标签页行为
    tab_context.select(refresh_context, inputs=[text_id,text_context_length,radio_context_type],outputs=[dataframe_context,text_refresh_id])
    
    # 文本框行为
    text_id.change(change_id, inputs = [text_id],
                outputs = [text_file_path,text_text,text_name,text_name_cn,text_gpt,text_baidu,text_final])
    text_final.change(change_final,inputs = [text_final,text_id])
    text_name_cn.change(change_name,inputs = [text_name,text_name_cn,text_id])
    
    # 按钮行为
    # -文本编辑页
    button_load_pos.click(load_last_position,inputs=text_file_path, outputs = text_id)
    if not if_save_id_immediately:
        button_save_pos.click(save_last_position, inputs = [text_id])
    button_up.click(last_text, outputs = text_id)
    button_down.click(next_text, outputs = text_id)
    button_translate_gpt.click(gpt_translate, 
                            inputs=[text_text,text_id], outputs=text_gpt)
    button_translate_baidu.click(baidu_translate, 
                                inputs=[text_text,text_id], outputs=text_baidu)
    button_replace.click(replace, 
                        inputs = [text_gpt,text_baidu,text_final,text_id], 
                        outputs=[text_gpt,text_baidu,text_final])
    button_save.click(save_json)
    
    button_batch_translate.click(batch_translate, inputs = [radio_translator,checkbox_if_save_translation,text_translate_start_id,text_translate_end_id],
                                 outputs = [label_progress])
    
    # -预览及导出页
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
    
    # -API管理页
    button_api_submit.click(submit_api, 
                            inputs = [text_baidu_api_id,text_baidu_api_key,text_from_lang,text_to_lang,
                                      text_openai_api,text_prefix,text_postfix])

demo.queue()

if __name__=="__main__":
    demo.launch(show_error=True)