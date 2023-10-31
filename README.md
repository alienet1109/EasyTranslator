# EasyTranslator 0.1.1-beta
基于gradio的汉化辅助工具
## 特性
1. 一键机翻接口，提供复制到剪贴板按钮。
2. 便捷的上下句切换，直接跳转功能。 
3. 记忆上次编辑位置功能。 
4. 人名翻译记忆功能，一次修改将会同步到全体。
5. 文本翻译记忆功能，机翻/修改后只要不关闭程序，切换上下句，刷新网页都不会影响译文缓存。相对地原文不会缓存，所以手滑改或删掉只要切换或者刷新即可恢复。
6. 一键替换功能，用于专有名词错译的情况。会将机翻及手翻文本中的对象全部替换。替换词典可以在运行中直接更改，不用重开程序。
7. 便利的api key管理及自动存储功能
8. 提供JSON文件与CSV文件互转
<br><br>

## 使用
至少需要安装python3(作者使用的版本是3.10，其它版本尚未测试)
***
### Install
```
git clone https://github.com/alienet1109/EasyTranslator.git
```
不想安git可以直接下载压缩包
***
### Preparation
#### 文本准备
需要使用者自行准备原文本json文件，或使用本程序将原文本csv文件转换为json文件
csv文件格式要求为：
* 至少包含人名列、文本列，按顺序排列的表格 

若不指定id列名，程序会自动生成id。 \
可以指定人名和文本的列名，将会分别以'name'、'text'为键输入json文件；其它列将会以原列名为键输入，以防数据丢失。

json文件格式要求为：
* 由key为id，value为{'name':'原文人名','text':'原文文本'}的键值对组成，按文本顺序正序排序的字典。

运行途中会频繁修改json文件，所以最好做好备份。\
可以随时在页面中修改json文件路径，修改前务必保存，修改后请按Load按钮以同步更新否则不知道会有什么bug。\
上次编辑文本编号将会重置，路径与编号将直接更新至config文件。

#### 安装依赖
```
pip install -r requirements.txt
```
#### 修改配置文件`config.json`
必须：
1. 设置文本文件("file_path")及人名词典("name_dict_path")的路径(推荐使用绝对路径)。之后结果会直接保存至对应路径。

可选：
1. 设置替换词典("replace_dict_path")路径，如不使用此功能则不需要；
2. 可设置api key和分隔符等，也可以直接在程序更改。程序中的修改会改变预设api key，但不会改变预设的分隔符。
***
### Run
直接点开`EasyTranslator.py`或在文件夹下执行命令:
```
python EasyTranslator.py
```
然后在网页中打开程序给出的网址（eg: http://127.0.0.1:7860）
<br><br>

## 演示

![image](https://github.com/alienet1109/EasyTranslator/blob/master/assets/id%20search.gif)

![image](https://github.com/alienet1109/EasyTranslator/blob/master/assets/name.gif)

![image](https://github.com/alienet1109/EasyTranslator/blob/master/assets/last%26next%20text.gif)

![image](https://github.com/alienet1109/EasyTranslator/blob/master/assets/replace.gif)

![image](https://github.com/alienet1109/EasyTranslator/blob/master/assets/api%20key%20setting.gif)

![image](https://github.com/alienet1109/EasyTranslator/blob/master/assets/derive%20text.gif)

## 计划追加功能
1. 可选主题
2. 追加翻译接口
3. 追加文本输出格式