import time
import requests
import PyPDF2
import re
import os

import time
import subprocess
import multiprocessing
from openai import OpenAI
import openai
from loguru import logger
import requests
import json

def ping():
    while True:
        requests.get("http://101.133.161.204:23333/ping")
        time.sleep(30)

def build_messages(prompt, history, system):
    messages = [{'role': 'system', 'content': system}]
    for item in history:
        messages.append({'role': 'user', 'content': item[0]})
        messages.append({'role': 'system', 'content': item[1]})
    messages.append({'role': 'user', 'content': prompt})
    return messages

def call_kimi(prompt, history=[]):
    client = OpenAI(
        api_key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=',
        base_url='https://api.moonshot.cn/v1',
    )

    SYSTEM = '你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一些涉及恐怖主义，种族歧视，黄色暴力，政治宗教等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。'  # noqa E501
    messages = build_messages(prompt=prompt,
                                history=history,
                                system=SYSTEM)

    logger.debug('remote api sending: {}'.format(messages))
    completion = client.chat.completions.create(
        model='moonshot-v1-32k',
        messages=messages,
        temperature=0.3,
    )
    return completion.choices[0].message.content

def callback_txt(filename):

    url = "http://101.133.161.204:23333/upload"

    files = {
        'file': open(filename, 'rb')  # 打开二进制文件
    }
    r = requests.post(url, files=files)
    print(r.text)

def gen_txt():
    resp = requests.get('http://101.133.161.204:23333/get')
    result = resp.text # 获取返回的结果,例如2401.08772

    if len(result) < 3:
        return None

    # 从arxiv下载pdf
    if not os.path.exists(f'{result}.pdf'):
        url = f'https://arxiv.org/pdf/{result}.pdf' 
        resp = requests.get(url)
        with open(f'{result}.pdf', 'wb') as f:
            f.write(resp.content) 
        
    # 用pyPDF读取PDF内容
    pdf_reader = PyPDF2.PdfReader(f'{result}.pdf')

    output = []
    stop = False
    for page in pdf_reader.pages:
        text = page.extract_text()
        prompt = '"{}"\n请仔细阅读以上内容，翻译成中文'.format(text)
        zh_text = call_kimi(prompt=prompt)
        output.append(zh_text)
        # output.append(text)
    
    txt_filepath = f'{result}.txt'
    with open(txt_filepath, 'w') as f:
        f.write('\n'.join(output))

    # 更新文本状态
    callback_txt(txt_filepath)
    return result


def gen_mp3(arxiv_id: str):
    content = ''
    txt_path = f'{arxiv_id}.txt'
    mp3_path = os.path.join('mp3', f'{arxiv_id}.mp3')

    if not os.path.exists(mp3_path):
        from paddlespeech.cli.tts.infer import TTSExecutor
        tts = TTSExecutor()

        with open(txt_path) as f:
            content = f.read()
        tts(content, mp3_path)
        # lines = content.split('\n')
        # group_lines = [lines[i:i+40] for i in range(0, len(lines), 40)]

        # filenames = []
        # for idx, group_line in enumerate(group_lines):
        #     filename = '{}.mp3'.format(idx)
        #     print(len(group_line))
        #     tts(text=''.join(group_line), output=filename)
        #     filenames.append(filename)

        # # 合并成一个 mp3
        # with open('concat.txt') as f:
        #     f.write('\n'.join(filenames))

        # os.system('ffmpeg -f concat -safe 0 -i concat.txt -c copy {}.mp3'.format(arxiv_id))
        
    url = "http://101.133.161.204:23333/upload"
    files = {
        'file': open(mp3_path, 'rb')  # 打开二进制文件
    }
    r = requests.post(url, files=files)
    print('mp3 upload')
    print(r.text)

    data = {
        "id": arxiv_id,
        "state": 'success',
        "txt_url": txt_path,
        "mp3_url": mp3_path 
    }

    url = "http://101.133.161.204:23333/set"
    headers = {
        "Content-Type": "application/json" 
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)
    print(response.text)

if __name__ == '__main__':
    # 保活进程
    p = multiprocessing.Process(target=ping)
    p.start()

    while True:
        arxiv_id = gen_txt()
        if arxiv_id is None or len(arxiv_id) < 6:
            time.sleep(10)
            print('sleep')
            continue

        callback_txt('2401.08772.txt')
        gen_mp3('2401.08772')
