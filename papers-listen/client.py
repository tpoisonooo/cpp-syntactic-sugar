import time
import requests
import PyPDF2
import re
import os
import pdb

import time
import subprocess
import multiprocessing
from openai import OpenAI
import openai
from loguru import logger
import requests
import json
from xunfei_tts import create_tts_task, query_and_download, TaskRecord
from paper import build_paper
from multiprocessing import Pool

record = TaskRecord()

def ping():
    requests.get("http://127.0.0.1:23333/ping")

def build_messages(prompt, history, system):
    messages = [{'role': 'system', 'content': system}]
    for item in history:
        messages.append({'role': 'user', 'content': item[0]})
        messages.append({'role': 'system', 'content': item[1]})
    messages.append({'role': 'user', 'content': prompt})
    return messages

def call_kimi(prompt):
    client = OpenAI(
        api_key='xxxxxxxxxxxxxxxxxxxxxxxxxxxx=',
        base_url='https://api.moonshot.cn/v1',
    )

    SYSTEM = '你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一些涉及恐怖主义，种族歧视，黄色暴力，政治宗教等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。'  # noqa E501
    messages = build_messages(prompt=prompt,
                                history=[],
                                system=SYSTEM)

    logger.debug('remote api sending')
    completion = client.chat.completions.create(
        model='moonshot-v1-128k',
        messages=messages,
        temperature=0.3,
    )
    return completion.choices[0].message.content

def translate(page):
    def remove_bracketed_content(text):
        result = []
        bracket_count = 0
        for char in text:
            if char == '(':
                bracket_count += 1
            elif char == ')':
                if bracket_count > 0:
                    bracket_count -= 1
                else:
                    # 如果没有匹配的开括号，则放弃匹配并返回原始字符串
                    return text
            elif bracket_count == 0:
                result.append(char)  # 如果不在括号内，则保留字符
        # 如果所有括号都匹配，则返回修改后的字符串
        return ''.join(result)

    text = page.extract_text()
    text = remove_bracketed_content(text)
    prompt = '"{}"\n请仔细阅读以上内容，翻译成中文'.format(text)
    zh_text = ""
    try:
        zh_text = call_kimi(prompt=prompt)
    except Exception as e:
        print(e)
        zh_text = '这部分触发了 LLM 安全检查，跳过本页。'
    # zh_text = '这里是中文翻译'
    # return '{}\n{}'.format(zh_text, text)
    return '{}'.format(zh_text)

def callback_txt(arxiv_id):
    filename = f'{arxiv_id}.txt'
    url = "http://127.0.0.1:23333/upload"

    files = {
        'file': open(filename, 'rb')  # 打开二进制文件
    }
    r = requests.post(url, files=files)
    print(r.text)

def callback(arxiv_id: str, state: str, txt_url:str='', mp3_url:str='', cost:str='', title:str=''):
    # 错误的 pdf，返回失败
    data = build_paper(arxiv_id=arxiv_id, state=state, txt_url=txt_url, mp3_url=mp3_url, cost=cost, title=title)
    url = "http://127.0.0.1:23333/set"
    headers = {
        "Content-Type": "application/json" 
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)
    print(response.text)

def remove_references(pages):
    ret = []
    for page in pages:
        text = page.extract_text()

        ref_text = text.replace(' ','')
        if 'REFERENCES\n' in ref_text or 'References\n' in ref_text:
            # 到了引用部分，跳过
            ret.append(page)
            break
        else:
            ret.append(page)
    return ret

def gen_txt():
    resp = requests.get('http://127.0.0.1:23333/get')
    result = resp.text # 获取返回的结果,例如2401.08772
    txt_filepath = f'{result}.txt'

    if os.path.exists(txt_filepath):
        return result

    if len(result) < 3:
        return None

    # 从arxiv下载pdf
    logger.debug('start download pdf {}'.format(result))
    pdf_filepath = f'{result}.pdf'
    if not os.path.exists(pdf_filepath):
        life = 0
        while life < 3:
            try:
                url = f'https://arxiv.org/pdf/{result}.pdf' 
                resp = requests.get(url)
                with open(pdf_filepath, 'wb') as f:
                    f.write(resp.content)
                break
            except Exception as e:
                print(e)
                life += 1
                time.sleep(3)
        
        if not os.path.exists(pdf_filepath):
            callback(arxiv_id=arxiv_id, state='pdf_download_fail')
            return None
    
    # 用pyPDF读取PDF内容
    pdf_reader = PyPDF2.PdfReader(f'{result}.pdf')

    responses = []
    stop = False

    full_text = ''
    for page in pdf_reader.pages:
        full_text += page.extract_text()
    prompt = '"{}"\n总结一下这篇论文'.format(full_text)
    summary = ''
    try:
        summary = call_kimi(prompt=prompt)
    except Exception as e:
        summary = '总结论文时安全检查不通过，跳过。'
    responses.append(summary)

    pages = remove_references(pdf_reader.pages)

    with Pool(2) as p:
        results = [p.apply_async(translate, args=(page,)) for page in pages]
        responses += [res.get() for res in results]

    print('gen txt')
    with open(txt_filepath, 'w') as f:
        f.write('\n'.join(responses))

    # 更新文本状态
    callback_txt(result)
    return result

def cal_cost(arxiv_id: str):
    txt_path = f'{arxiv_id}.txt'
    pdf_path = f'{arxiv_id}.pdf'
    
    txt_len = 0
    with open(txt_path) as f:
        txt_len = len(f.read())

    pdf_reader = PyPDF2.PdfReader(pdf_path)
    full_text = ''
    for page in pdf_reader.pages:
        full_text += page.extract_text()
    
    llm_cost = (txt_len + 2 * len(full_text)) / 1000 / 2 * 0.06
    tts_cost = txt_len / 10000.0 * 3
    cost = round(llm_cost + tts_cost + 0.1, 2)
    desc = '，字数{}，LLM {}，TTS {}'.format(len(full_text), round(llm_cost,2), round(tts_cost,2))
    return str(cost) + desc

def get_title(arxiv_id: str):
    pdf_path = f'{arxiv_id}.pdf'
    title = PyPDF2.PdfReader(pdf_path).pages[0].extract_text().split('\n')[0]
    if len(title) > 50:
        title = title[0:48].strip() + '..'
    return title

def gen_mp3(arxiv_id: str):
    txt_path = f'{arxiv_id}.txt'
    mp3_path = f'{arxiv_id}.mp3'

    if not os.path.exists(mp3_path):
        print(f'{mp3_path} not found')
        if not record.get(arxiv_id):
            # 拿任务 ID
            task_id = create_tts_task(txt_path)
            if task_id is None:
                callback(arxiv_id, 'tts_create_fail')
                return
            record.add(arxiv_id, task_id)
            callback(arxiv_id, 'tts_wait')
            query_and_download(task_id, mp3_path)
        else:
            # 第二次过来，尝试问结果
            task_id, create_time = record.get(arxiv_id)
            if time.time() - create_time > 3600:
                # 过时任务，返回失败
                logger.error(f'{arxiv_id} timeout')
                callback(arxiv_id, 'tts_timeout')
            else:
                query_and_download(task_id, mp3_path)

    if not os.path.exists(mp3_path):
        return
    # 成功，返回结果
    url = "http://127.0.0.1:23333/upload"
    files = {
        'file': open(mp3_path, 'rb')  # 打开二进制文件
    }
    r = requests.post(url, files=files)
    print('mp3 upload')
    print(r.text)

    cost = cal_cost(arxiv_id)
    title = get_title(arxiv_id)
    callback(arxiv_id, state='success', txt_url=txt_path, mp3_url=mp3_path, cost=cost, title=title)


if __name__ == '__main__':
    # 保活进程
    while True:
        ping()
        arxiv_id = gen_txt()
        if arxiv_id is None or len(arxiv_id) < 6:
            time.sleep(6)
            print('sleep')
            continue

        gen_mp3(arxiv_id)
