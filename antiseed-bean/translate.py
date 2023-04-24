# -*- coding: utf-8 -*-

# This code shows an example of text translation from English to Simplified-Chinese.
# This code runs on Python 2.7.x and Python 3.x.
# You may install `requests` to run this code: pip install requests
# Please refer to `https://api.fanyi.baidu.com/doc/21` for complete api document

import requests
import random
import json
from hashlib import md5
import time
import os

# Generate salt and sign
def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()

def translate(query: str):
    # Set your own appid/appkey.
    appid = '20230331001622606'
    appkey = 'Tm48tDL3Ho9s9pSXvoMg'

    # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
    from_lang = 'en'
    to_lang =  'zh'

    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path

    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)

    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

    # Send request
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()
    print(result)
    result = result['trans_result']

    outputs = []
    for r in result:
        outputs.append(r['dst'])
    
    time.sleep(0.11)
    return '\n'.join(outputs)

# print(translate("Give three tips for staying healthy. | | 1. Eat a balanced diet and make sure to include plenty of fruits and vegetables. \n2. Exercise regularly to keep your body active and strong. \n3. Get enough sleep and maintain a consistent sleep schedule."))

import ijson
import json

save = dict("")

count = 0

with open('alpaca_data_cleaned.json', 'r') as file:
    parser = ijson.parse(file)
    for prefix, event, value in parser:
        unit = dict()
        for item in parser:
            # 处理每个元素

            if item[0] == 'item.instruction':
                if 'instruction' in unit:
                    raise Exception(item)
                unit['instruction'] = item[2]

            elif item[0] == 'item.input':
                unit['input'] = item[2]
            elif item[0] == 'item.output':
                unit['output'] = item[2]

            print(item[0])
            if item[0] == 'item.output':
            # if len(unit) >= 3:
                # hash and translate
                count += 1
                sign = make_md5(json.dumps(unit))
                filepath = os.path.join('alpaca_data_zhcn', sign)

                with open('filelist.txt', 'a') as f:
                    f.write(sign)
                    f.write('\n')

                if os.path.exists(filepath):
                    # skip
                    unit = dict()
                    print('skip {}'.format(filepath))
                    continue
                
                trans = dict()
                keys = ['instruction', 'input', 'output']
                for key in keys:
                    q = unit[key]
                    if len(q) <= 1:
                        trans[key] = q
                    else:
                        trans[key] = translate(unit[key])
                with open(filepath, 'w', encoding='utf8') as f:
                    json.dump(trans, f, indent=2, ensure_ascii=False)

                unit = dict()

print('count = {}'.format(count))
