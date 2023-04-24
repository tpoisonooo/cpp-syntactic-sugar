# 提取聊天消息里，可直接获取的引用消息。转成训练格式
# instruction input output
import os
import json
import xml
import xml.etree.ElementTree as ET

def remove_newline(text):
    return ' '.join(text.split('\n'))

zhdatas = []
for dirpath, dirnames, files in os.walk('./alpaca_data_zhcn'):
    for _file in files:
        filepath = os.path.join(dirpath, _file)
        print('processing {}\n'.format(filepath))
        with open(filepath) as f:
            data = json.load(f)
            zhdatas.append(data)

with open('zhdata.json', 'w', encoding='utf8') as f:
    json.dump(zhdatas, f, indent=2, ensure_ascii=False)
