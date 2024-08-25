from flask import Flask, request, send_file, render_template, abort
import redis
import os
import requests
import re
from paper import build_paper
app = Flask(__name__)
redis = redis.Redis(host='localhost', port=6379, db=1, charset="utf-8", decode_responses=True)

def build_result(suggestion:list = [], target:object = None):
    online = '<div><label class="blue-text">服务在线 23333 </label></div>'
    ping = redis.get('ping')
    if ping is None or len(ping) < 1:
        online = '<div><label class="red-bold-text">服务失连，别着急，作者会看。</label></div>'

    html_template_part0 = '''
<!DOCTYPE html>
<style>
    .btn {
        width: 30vw;
        height: auto;
	align-items: center;
    }
    .red-bold-text {
        color: red;
        font-weight: bold;
    }
    .blue-text {
        color: blue;
        font-weight: bold;
    }
    .container {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    img {
        width: 50vw;
        height: auto;
    }
</style>
<html>
<head>
    <title> arxiv 睡前听书 </title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
'''
    html_template_part1 = '''
    <h2> arxiv 翻译并转 mp3 </h2>
    <div>
        <label> 第一步：打开 <a href="https://papers.cool/"> papers.cool</a> ，选个想听的论文 ID （如 2401.08772） </label>
    </div>
    <div>
    <label> 第二步：填写 arxiv ID（如 2401.08772），静待处理完成。一篇可能 10+ 分钟，具体看长度 </label>
    <form action="/new" method="new">

            <div>
                <label for="arxiv-id">arxiv ID:</label>
                <input type="string" id="arxiv-id" name="arxiv_id" value="">
                <button class="btn" type="submit">提交</button>
            </div>
'''

    html_template_part2 = '''
    </form>
    </div>
    <div>
        <label> 第三步：点击 “mp3” 到手机，开始听论文</label>
    </div>

<h4>计费说明</h4>
<div>* LLM 使用 kimi-chat，0.06 元/1 千 token。需 1 次总结和 1 次翻译，因此长度=英文输入* 2+中文输出</div>
<div>* 平均 2 中文字符计 1 个 token</div>
<div>* TTS 使用讯飞，3 元/万字。长度=中文输出</div>
<div>* 部署于阿里云，按量计费。计 0.1 元/论文</div>
'''

    html_template_part3 = '''
<h2><label class="red-bold-text">阿弥陀佛，自觉付费<label></h2>
<div class="container">
    <img src="https://deploee.oss-cn-shanghai.aliyuncs.com/zanshang.jpg" alt="赞赏码">
</div>
<h2><label">作者的其他小应用<label></h2>
<div>* <a href="https://github.com/internlm/huixiangdou">茴香豆</a>，群聊场景（如个人微信/飞书）领域知识助手。已面对数千人稳定运行半年，安全无幻觉</div>
<div>* <a href="http://101.133.161.204:9999/">提前还贷计算器</a>，看每月多还 2000，能少多少利息</div>
<div>* <a href="https://platform.openmmlab.com/deploee">硬件模型库</a>，CNN 时代的 onnx 模型库</div>
</body>
</html>
    '''

    target_str = ''
    if target is not None:
        target_str = '''
<div>
<table border="1">
<thead>
<tr>
<th>id</th> 
<th>状态</th>
<th>文本路径</th>
<th>语音地址</th>
<th>成本（元）</th>
</tr>
</thead>
<tbody>'''


        if target['state'] != 'success':
            target_str += '''
<tr>
<td> {} </td> 
<td> {} </td>  
<td> - </td>
<td> - </td>
<td> - </td>
</tr>
</tbody>
</table>
</div>'''.format(target['id'], target['state'])
        else:
            _id = target['id']
            title = target['title']
            if title is not None and len(title) > 0:
                _id += ' '
                _id += title

            target_str +='''
<tr>
<td>{}</td> 
<td>{}</td>  
<td><a href="/download/{}">txt</a></td>
<td><a href="/download/{}">mp3</a></td>
<td>{}</td>
</tr>
</tbody>
</table>
</div>
        '''.format(_id, target['state'], target['txt_url'], target['mp3_url'], target['cost'])

    papers_str = ''
    if len(suggestion) > 0:
        papers_str += '''
<h2> 任务列表 </h2>
<div>
<table border="1">
<thead>
<tr>
<th>id</th> 
<th>状态</th>
<th>文本路径</th>
<th>语音地址</th>
<th>成本（元）</th>
</tr>
</thead>
<tbody>
        '''
        for paper in suggestion:
            if paper['state'] != 'success':
                papers_str += '''
<tr>
<td> {} </td> 
<td> {} </td>  
<td> - </td>
<td> - </td>
<td> - </td>
</tr>'''.format(paper['id'], paper['state'])

            else: 
                _id = paper['id']
                title = paper['title']
                if title is not None and len(title) > 0:
                    _id += ' '
                    _id += title

                papers_str += '''
<tr>
<td> {} </td> 
<td> {} </td>  
<td><a href="/download/{}"> txt </a></td>
<td><a href="/download/{}"> mp3 </a></td>
<td> {} </td>
</tr>'''.format(_id, paper['state'], paper['txt_url'], paper['mp3_url'], paper['cost'])
        
        papers_str += '''
</tbody></table></div>
'''
    
    return html_template_part0 + online + html_template_part1 + target_str + html_template_part2 + papers_str + html_template_part3


def check_format(string):
    pattern = r'^[0-9]{4}\.[0-9]{5}$'
    result = re.match(pattern, string) 
    if result:
        return True
    else:
        return False

# 提交新任务
@app.route('/new', methods=['GET'])
def load():
    # 使用 request.args.get() 来获取GET请求的参数
    arxiv_id = request.args.get('arxiv_id')
    arxiv_id = arxiv_id.strip()
    # 读 redis，看目标 arxiv 是否处理完成
    if len(arxiv_id) < 5:
        return '非法的 arxiv id : {}'.format(arxiv_id)
    
    if not check_format(arxiv_id):
        return 'arxiv id 检查不通过 {}'.format(arxiv_id)

    # 看前面还有多少个未处理完的
    keys =  redis.keys('paper:*')
    cnt = 0
    for key in keys:
        attrs = redis.hmget(key, 'state')
        if attrs[0] == 'processing':
            cnt += 1
    if cnt > 50:
        return '前面还有超过 50 个没处理，晚点再来吧'

    key = 'paper:{}'.format(arxiv_id)
    target = None
    attrs = redis.hmget(key, 'state', 'txt_url', 'mp3_url', 'cost')
    if attrs is None or len(attrs) < 1 or attrs[0] is None:
        # 如果不存在，创建个新的
        target = build_paper(arxiv_id=arxiv_id)
        redis.hmset(key, target)
    else:
        # 存在
        target = build_paper(arxiv_id=arxiv_id, state=attrs[0], txt_url=attrs[1], mp3_url=attrs[2], cost=attrs[3])
    
    # 列出所有 paper
    keys =  redis.keys('paper:*')
    keys = sorted(keys, reverse=True)[0:50]
    papers = []
    for key in keys:
        attrs = redis.hmget(key, 'state', 'txt_url', 'mp3_url', 'cost', 'title')
        paper = build_paper(arxiv_id=key.split(':')[-1], state=attrs[0], txt_url=attrs[1], mp3_url=attrs[2], cost=attrs[3], title=attrs[4])
        papers.append(paper)
    return build_result(suggestion=papers, target = target)


# 获取一个待处理的
@app.route('/get', methods=['GET'])
def get_paper():
    # 列出所有 paper
    ret = ''
    keys =  redis.keys('paper:*')
    for key in keys:
        attrs = redis.hmget(key, 'state')
        if attrs[0] == 'processing' or attrs[0] == 'tts_wait':
            ret = key.split(':')[-1]
            break
    return ret


# 设置处理状态
@app.route('/set', methods=['POST'])
def set_paper():
    try:
        paper = request.get_json()
        arxiv_id = paper['id']
        key = 'paper:{}'.format(arxiv_id)
        redis.hmset(key, paper)
    except Exception as e:
        print(e)
    return 'success'

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        files = request.files
        for _, f in files.items():
            f.save(os.path.join('uploads', f.filename))
    except Exception as e:
        print(e)
        return 'fail'
    return 'success'

@app.route("/ping", methods=["POST", "GET"])
def ping():
    redis.set('ping', 'pong', ex=1800)
    return 'pong'

@app.route("/download/<path:path>") 
def download(path):
    file_path = os.path.join('uploads', path)
    if not os.path.exists(file_path):
        abort(404)
    return send_file(file_path)

@app.route('/', methods=['GET'])
def index():
    keys =  redis.keys('paper:*')
    keys = sorted(keys, reverse=True)[0:50]
    papers = []
    for key in keys:
        attrs = redis.hmget(key, 'state', 'txt_url', 'mp3_url', 'cost', 'title')
        paper = build_paper(arxiv_id=key.split(':')[-1], state=attrs[0], txt_url=attrs[1], mp3_url=attrs[2], cost=attrs[3], title=attrs[4])
        papers.append(paper)
    return build_result(suggestion=papers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=23333)
