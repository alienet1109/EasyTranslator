# EasyTranslator 0.1.1-beta
自用为主的汉化辅助工具
## 特性
1. 一键机翻接口，提供复制到剪贴板按钮。
2. 便捷的上下句切换，直接跳转功能。 
3. 记忆上次编辑位置功能。 
4. 人名翻译记忆功能，一次修改将会同步到全体。
5. 文本翻译记忆功能，机翻/修改后只要不关闭程序，切换上下句，刷新网页都不会影响译文缓存。相对地原文不会缓存，所以手滑改或删掉只要切换或者刷新即可恢复。
6. 一键替换功能，用于专有名词错译的情况。会将机翻及手翻文本中的对象全部替换。替换词典可以在运行中直接更改，不用重开程序。
7. 手滑删或改掉了api key可以刷新，文本框会回到初始状态，再次提交即可。（其实是bug。但好像有好处先留着）
<br><br>

## 使用
至少需要安装python3(作者使用的版本是3.10。3.8和3.9目前测试没有问题)
***
### Install
```
git clone https://github.com/alienet1109/EasyTranslator.git
```
不想安git可以直接下载压缩包
***
### Preparation
#### 文本准备
需要使用者自行准备原文本json文件。逻辑是运行途中就会修改json文件所以最好做好备份。

格式要求为：
* 由key为id，value为{'name':'原文人名','text':'原文文本'}的键值对组成，按文本顺序正序排序的字典。

之后预计会追加将csv/txt文件转为json的功能。
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
