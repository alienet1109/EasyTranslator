# EasyTranslator v1.1.0
基于gradio的汉化辅助工具

## 使用
至少需要安装python3(作者使用的版本是3.10, 其它版本尚未测试)
***
### Install
```
git clone https://github.com/alienet1109/EasyTranslator.git
```
不想安git可以直接下载压缩包
***
### Preparation
#### 1. 安装依赖
```
pip install -r requirements.txt
```
#### 2. 文本准备
原始文本可为JSON或CSV格式（若使用CSV格式，需要首先使用本程序的转换功能将其转为JSON格式）。

**CSV文件格式**

1. **必需列**:
   - `name`: 人名列，可为空。
   - `text`: 文本列

2. **列名规范**:
   - 默认使用 `name` 和 `text` 作为关键列
   - 如果没有人名，可以在CSV中创建空的 `name` 列
   - 若文件中有其他额外列，将保留原始列名，防止数据丢失

3. **ID生成**:
   - 若CSV文件中包含`id`列，则使用该列作为id，请确保该列没有重复值。
   - 如果未指定ID列，程序将自动生成ID

**JSON文件格式**

JSON文件应满足以下结构：
- 使用 `id` 作为键
- 值为包含 `name` 和 `text` 的字典
- 按文本顺序正序排序

#### JSON文件示例
```json
{
    "001001": {"name": "A", "text": "第一段文本"},
    "001002": {"name": "B", "text": "第二段文本"}
}

#### 3. 修改配置文件`config.json`
* 必须：
    1. 设置文本文件`file_path`及人名词典`name_dict_path`的路径(推荐使用绝对路径)。之后结果会直接保存至对应路径。

* 可选：
    1. 设置替换词典`replace_dict_path`路径, 如不使用此功能则不需要；
    2. 可设置api key和分隔符等, 也可以直接在程序更改。程序中的修改会改变预设api key, 但不会改变预设的分隔符。
***
### Run
直接点开`EasyTranslator.py`或在文件夹下执行命令:
```
python EasyTranslator.py
```
然后在网页中打开程序给出的网址（eg: http://127.0.0.1:7860 ）
<br><br>

## v1.1.0更新内容
1. 现支持通常翻译和批量翻译中gemini, claude, qwen, deepseek...等模型的自由选择和调用。请在`config.json`中或API页填写api key (注：当设置了OpenRouter的api时，会优先使用OpenRouter的接口)。使用gemini, claude, doubao等的官方接口请安装相关依赖包。可以自行修改`utils.py`中的MODEL_LIST以调整可选模型，避免冗余。
2. 修改了键盘快捷键设置<br>
    alt+w: ↑<br>
    alt+x: ↓<br>
    alt+s: save json<br>
    alt+r: replace<br>
    alt+q: model1 translate<br>
    alt+e: model2 translate<br>

## v1.0.6更新内容
1. 更新文件合并功能，方便多人协作。在文件合并页中可将依照指示将两个json文件合并，同步人工翻译进度。并支持导出小规模json文件方便传输。

## v1.0.5更新内容
1. 支持键盘快捷键

## v1.0.4更新内容
1. 追加摸鱼模式, 将必要组件集中在半个屏幕内。在`config.json`中`moyu_mode`设为1开启, 设为0关闭
2. 加入对GPT翻译的超时检测, 时间上限在`config.json`的`openai_api_settings`中的`time_limit`处设置, 单位为秒。若请求超时, 会打印超时提示, 但不会报错）
3. GPT翻译现在将不返回重复结果

## v1.0.3更新内容
1. 支持预览页直接修改译文, 建议保存JSON后再使用此功能
2. 可选是否即时更新上次编辑id

    `config.json`中设置`"if_save_id_immediately"`参数, 若为1则逻辑与之前一样, 在切换id时立刻保存进`config.json`；若为0则会显示保存编辑id按钮`SAVE last edited position`, 在点击后存入`config.json`。

## v1.0.2更新内容
1. 支持批量机翻

## v1.0.1更新内容
1. 优化文件读取逻辑
2. 增加错误提示、警告等。保存JSON成功时会提示更新的译文条数
3. 允许自定义传输到gpt的prompt、自定义百度翻译的原文及目标语言
4. 追加上下文预览功能, 并允许自定义预览条数和编号。指定id将会以双星号标记, 修改过的译文将会在前面加星号标记
5. 优化按钮手感

## 特性
1. 一键机翻接口, 提供复制到剪贴板按钮
2. 便捷的上下句切换, 直接跳转功能
3. 记忆上次编辑位置功能
4. 人名翻译记忆功能, 一次修改将会同步到全体。人名词典在程序启动时读取并在保存JSON文件时保存。开启程序时可以直接改`name_cn`, 关闭程序后可以修改人名词典。下次开启程序时人名词典中的内容将会覆盖JSON文件中的`name_cn`。
5. 文本翻译记忆功能, 机翻/修改后只要不关闭程序, 切换上下句, 刷新 网页都不会影响
6. 译文缓存。相对地原文不会缓存, 所以手滑改或删掉只要切换或者刷新即可恢复。因此想查看原文具体某个词的翻译也可以直接编辑原文再机翻, 不会影响原文本。
7. 一键替换功能, 用于专有名词错译的情况。会将机翻及手翻文本中的对象全部替换。替换词典可以在运行中直接更改, 不用重开程序。
8. 便利的api key管理及prompt修改等
9. 提供JSON文件与CSV文件互转
10. 上下文预览功能
<br><br>


## 演示
摸鱼模式 \
![image](https://github.com/alienet1109/EasyTranslator/blob/master/assets/moyu_mode.png) \
批量翻译 \
![image](https://github.com/alienet1109/EasyTranslator/blob/master/assets/batch_translate.gif) \
上下文预览\
![image](https://github.com/alienet1109/EasyTranslator/blob/master/assets/context_preview.gif) 

![image](https://github.com/alienet1109/EasyTranslator/blob/master/assets/id%20search.gif)

![image](https://github.com/alienet1109/EasyTranslator/blob/master/assets/name.gif)

![image](https://github.com/alienet1109/EasyTranslator/blob/master/assets/last%26next%20text.gif)

![image](https://github.com/alienet1109/EasyTranslator/blob/master/assets/replace.gif)

![image](https://github.com/alienet1109/EasyTranslator/blob/master/assets/api%20key%20setting.gif)

![image](https://github.com/alienet1109/EasyTranslator/blob/master/assets/derive%20text.gif)

![image](https://github.com/alienet1109/EasyTranslator/blob/master/assets/part_translate.gif)

## 计划追加功能
1. 可选主题
2. 追加翻译接口
3. 追加文本输出格式
4. 发生修改时直接存入小规模临时文件, 防止数据丢失
