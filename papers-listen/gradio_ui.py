import gradio as gr
import redis
import json
from paper import Paper, RedisStorage
import xml.etree.ElementTree as ET

# 连接 Redis
redis_client = redis.Redis(host='localhost', port=6380, password='hxd123', decode_responses=True)

# 转换论文状态的函数
def notify_convert_paper(xml_content):
    root = ET.fromstring(xml_content)
    # 找到第一个<td>标签并获取其内容
    arxiv_id = root.find('.//td').text
    arxiv_id = arxiv_id.strip()
    notify_rs = RedisStorage()
    notify_rs.add_task(arxiv_id)
    notify_rs.update_paper_status(arxiv_id, 'pending')
    return '处理中'

# 创建 Gradio 界面
def create_ui():

    html_line_template = """
<table border="1" style="width: 100%; table-layout: fixed;">
<thead>
<tr>
<td id="arxiv_id" style="width: 10%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"> {} </td> 
<td style="width: 70%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"> {} </td>  
<td style="width: 20%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"> {} </td>
</tr>
</thead>
</table>
    """

    rs = RedisStorage()
    papers = rs.get_top_n()

    with gr.Blocks() as demo:
        # header
        gr.Markdown("""
# arxiv 听书
从 [arxiv.org cs.AI/cs.CL](arxiv.org) 拉取每日 arxiv 更新，从 [papers.cool](https://papers.cool/) 获取文本，转换成 mp3 播放。

解放酸痛的眼睛，适合**睡前**、**跑步**、**带娃**等生活场景。把读论文当作一种消遣。

## 用法
选择想听的论文，点击 “提交” 即可（预计 10 分钟）。**谁提交，谁付费**，首页会放其他人提交的、concat 后的 mp3 大合集。

* LLM 用 [kimi](https://kimi.moonshot.cn/), 
    * 调用前会 check 一下苏神那边有木有现成结果, 没有就调自己的 LLM API
* TTS 用迅飞, 3 元/万字

## 列表""")

        # 论文
        for paper in papers:

            with gr.Row():
                with gr.Column(scale=5):
                    html_line = html_line_template.format(paper.arxiv_id, paper.title, paper.note)
                    html = gr.HTML(html_line)

                with gr.Column(scale=1):
                    status = paper.status
                    print(status)
                    if status == 'init':
                        btn = gr.Button("转换")
                        btn.click(fn=notify_convert_paper, inputs=html, outputs=btn)
                    elif status == 'success':
                        gr.Markdown(paper.mp3_url)
                    elif status == 'error':
                        gr.HTML('<table><tr><td style="color: red;">{}</td></tr></table>'.format(status))
                    else:
                        gr.HTML('<table><tr><td style="color: green;">{}</td></tr></table>'.format(status))
    
        # tail
        tail_html="""
<h2><label style="color: red; font-weight: bold;">阿弥陀佛，自觉付费<label></h2>
<div style="display: flex; justify-content: center; align-items: center;">
    <img src="https://deploee.oss-cn-shanghai.aliyuncs.com/zanshang.jpg" alt="赞赏码">
</div>"""
        gr.HTML(tail_html)
        gr.Markdown("""
## 作者的其他应用
* [HuixiangDou](https://github.com/internlm/huixiangdou) 专家知识助手，支持**群聊**（如个人微信/飞书）和实时流式响应 2 类场景
* [硬件模型库](https://platform.openmmlab.com/deploee) CNN 时代的 onnx 模型库
* [提前还贷计算器](http://101.133.161.204:9999) 每月多还 2000，能省多少利息
""")
    return demo

# 启动 Gradio 界面
if __name__ == "__main__":
    ui = create_ui()
    ui.launch()
    