# coding=UTF-8
from flask import Flask, request, jsonify
from loguru import logger
import requests, json
import xml.etree.ElementTree as ET

app = Flask(__name__)

with open('me.txt') as f:
    me = json.load(f)
    mywxid = me['wcId']
    print('I am {}'.format(mywxid))

def send(wid, group, content, title):
    with open('send.txt', 'a') as f:
        jsonstr = json.dumps({"wid": wid, 'group': group, 'content': content, 'title': title}, indent=2)
        jsonstr = jsonstr.encode('utf8').decode('unicode_escape')
        f.write(jsonstr)
        f.write('\n')

    auth = ''
    with open('auth.txt') as f:
        auth = f.read()

    headers = {
       "Content-Type": "application/json",
       "Authorization": auth
    }
    data = {
        "wId": wid,
        "wcId": group,
        "content": content
    }

    resp = requests.post('http://114.107.252.79:9899/sendText', data=json.dumps(data), headers = headers)
    print(resp, resp.content)
    if resp.status_code == 200:
        return True
    else:
        return False

def ok():
    return jsonify({})

def parseXML(xmlstr):
    content = None
    try:
        root = ET.fromstring(xmlstr)
        content = root.find('appmsg/refermsg/content').text
        fromuser = root.find('appmsg/refermsg/fromusr').text
    except:
        return None, None
    return fromuser, content

def getResponse(content, title):
    data = {"fn_index":0,"data":["{} {}".format(content, title)]}
    resp = requests.post('https://3c04f31e3c1769ad87.gradio.live/run/predict', data=json.dumps(data))
    print(resp, resp.content)
    x = json.loads(resp.content)
    x = x['data']
    if type(x) == list:
        return x[0]
    return x

@app.route('/callback', methods=['GET', 'POST'])
def callback():

    x = request.get_json()
    messageType = x['messageType']
    if messageType != '80001' and messageType != '80014':
        print('{}'.format(messageType))
        return ok()

    data = x['data']
    if data['self']:
        return ok()

    with open('history.txt', 'a') as f:
        jsonstr = json.dumps(x, indent=2)
        jsonstr = jsonstr.encode('utf8').decode('unicode_escape')
        f.write(jsonstr)
        f.write('\n')

    # 瓜球
    whitelist = ['wxid_raxq4pq3emg212', 'wxid_nl9mlgj0juta21']

    if messageType == '80014':
        target = data['toUser']
        if target == mywxid:
            wid = data['wId']
            group = data['fromGroup']
            title = data['title'][4:]
            content = data['content']
            fromuser, content = parseXML(content)
            if fromuser in whitelist and content is not None:

                resp = getResponse(title, content)
                send(wid, group, resp, title)
            else:
                logger.debug('fromuser {} say {} banned'.format(fromuser, content))
    elif messageType == '80001':
        fromuser = data['fromUser']
        wid = data['wId']
        content = data['content']
        group = data['fromGroup']
        title = ''

        if fromuser in whitelist and content.startswith("@茴香豆"):
            content = content[4:]
            resp = getResponse(title, content)
            send(wid, group, resp, title)
        elif group == '18356748488@chatroom' or group == '18356748488@chatroom':
            if "@茴香豆" in content:
                content = content[4:]
                resp = getResponse(title, content)
                send(wid, group, resp, title)
    return ok()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
