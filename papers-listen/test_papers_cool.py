import requests
import xml.etree.ElementTree as ET
import markdown
import pdb
import re

def convert_papers_cool_to_html(url):
    # 获取内容
    # 1. 移除 xml 壳
    # 2. 移除 markdown 壳
    response = requests.get(url)
    response.raise_for_status()  # 确保请求成功
    html_content = response.text

    pattern_q = r"<p class=\"faq-q\"><strong>Q</strong>: (.*?)<\/p>"
    pattern_a = r"<p class=\"faq-a\"><strong>A</strong>: (.*?)<\/p>"

    # 打印匹配项
    qs = []
    _as = []
    for match in re.findall(pattern_q, html_content, re.DOTALL):
        qs.append(match)

    for match in re.findall(pattern_a, html_content, re.DOTALL):
        _as.append(match)
    
    pairs = []
    size = max(1, min(len(qs), len(_as)))

    text = ''
    for i in range(size - 1):
        text += qs[i]
        text += '\n'
        text += _as[i]
        text += '\n'
        # pairs.append(qs[i], _as[i])
    print(text)

pairs = convert_papers_cool_to_html('https://papers.cool/arxiv/kimi?paper=2408.82579')
