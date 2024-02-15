from flask import Flask, request, send_file, render_template, abort
import redis
import os

app = Flask(__name__)
redis = redis.Redis(host='localhost', port=6379, db=1, charset="utf-8", decode_responses=True)

def build_result(suggestion:list = [], target:object = None):
    online = '<div><label class="blue-text">后端服务在线..</label></div>'
    ping = redis.get('ping')
    if ping is None or len(ping) < 1:
        online = '<div><label class="red-bold-text">后端服务失连!!</label></div>'

    html_template_part0 = '''
<!DOCTYPE html>
<style>
    .btn {
        width: 10vw;
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
        width: 30vw;
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
    <h2> arxiv 对照翻译并转 mp3 </h2>
    <div>
        <label> 第一步：打开 <a href="https://papers.cool/"> papers.cool</a> ，选个想听的论文 ID （如 2401.08772） </label>
    </div>
    <div>
    <label> 第二步：填写 arxiv ID，等待处理完成 </label>
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
        <label> 第三步：点击 “mp3 下载”到手机，开始听论文</label>
    </div>
'''

    html_template_part3 = '''
<h3>打赏作者，留言解锁更多功能</h3>
<div class="container">
    <img src="https://deploee.oss-cn-shanghai.aliyuncs.com/zanshang.jpg" alt="赞赏码">
</div>
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
<th>mp3 下载地址</th>
</tr>
</thead>
<tbody>'''


        if target['state'] == 'processing':
            target_str += '''
<tr>
<td> {} </td> 
<td> {} </td>  
<td> - </td>
<td> - </td>
</tr>
</tbody>
</table>
</div>'''.format(target['id'], target['state'])
        else:
            target_str +='''
<tr>
<td>{}</td> 
<td>{}</td>  
<td><a href="/download/{}">txt</a></td>
<td><a href="/download/{}">mp3</a></td>
</tr>
</tbody>
</table>
</div>
        '''.format(target['id'], target['state'], target['txt_url'], target['mp3_url'])

    papers_str = ''
    if len(suggestion) > 0:
        papers_str += '''
<h2> 推荐的论文列表 </h2>
<div>
<table border="1">
<thead>
<tr>
<th>id</th> 
<th>状态</th>
<th>文本路径</th>
<th>mp3 下载地址</th>
</tr>
</thead>
<tbody>
        '''
        for paper in suggestion:
            if paper['state'] == 'processing':
                papers_str += '''
<tr>
<td> {} </td> 
<td> {} </td>  
<td> - </td>
<td> - </td>
</tr>'''.format(paper['id'], paper['state'])

            else: 
                papers_str += '''
<tr>
<td> {} </td> 
<td> {} </td>  
<td><a href="/download/{}"> txt </a></td>
<td><a href="/download/{}"> mp3 </a></td>
</tr>'''.format(paper['id'], paper['state'], paper['txt_url'], paper['mp3_url'])
        
        papers_str += '''
</tbody></table></div>
'''
    
    return html_template_part0 + online + html_template_part1 + target_str + html_template_part2 + papers_str + html_template_part3

# 提交新任务
@app.route('/new', methods=['GET'])
def load():
    # 使用 request.args.get() 来获取GET请求的参数
    arxiv_id = request.args.get('arxiv_id')
    # 读 redis，看目标 arxiv 是否处理完成
    if len(arxiv_id) < 5:
        return '非法的 arxiv id : {}'.format(arxiv_id)
    
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
    attrs = redis.hmget(key, 'state', 'txt_url', 'mp3_url')
    if attrs is None or len(attrs) < 1 or attrs[0] is None:
        # 如果不存在，创建个新的
        target = {'id': arxiv_id, 'state': 'processing', 'txt_url': '-', 'mp3_url': '-'}
        redis.hmset(key, target)
    else:
        # 存在
        target = {'id': arxiv_id,'state': attrs[0], 'txt_url': attrs[1], 'mp3_url': attrs[2]}
    
    # 列出所有 paper
    keys =  redis.keys('paper:*')
    keys = sorted(keys, reverse=True)[0:50]
    papers = []
    for key in keys:
        attrs = redis.hmget(key, 'state', 'txt_url', 'mp3_url')
        if attrs[0] == 'success':
            paper = {'id': key.split(':')[-1], 'state': attrs[0], 'txt_url': attrs[1], 'mp3_url': attrs[2]}
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
        if attrs[0] == 'processing':
            ret = key.split(':')[-1]
            break
    return ret

# 设置处理状态
@app.route('/set', methods=['POST'])
def set_paper():
    try:
        paper = request.get_json()
        arxiv_id = paper['id']
        state = paper['state']
        txt_url = paper['txt_url']
        mp3_url = paper['mp3_url']
        key = 'paper:{}'.format(arxiv_id)
        redis.hmset(key, {'id': arxiv_id, 'state': state, 'txt_url': txt_url, 'mp3_url': mp3_url})
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
    redis.set('ping', 'pong', ex=120)
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
        attrs = redis.hmget(key, 'state', 'txt_url', 'mp3_url')
        if attrs[0] == 'success':
            paper = {'id': key.split(':')[-1], 'state': attrs[0], 'txt_url': attrs[1], 'mp3_url': attrs[2]}
            papers.append(paper)
    return build_result(suggestion=papers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=23333)

