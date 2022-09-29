# -*- coding:utf-8 -*-
from flask import Flask, request, jsonify
from utils import lark_webhook, issue_comment, github_token
import json

import os
import requests
import json
import logging
import time
import urllib
import urllib3
import datetime
urllib3.disable_warnings()


try:
    JSONDecodeError = json.decoder.JSONDecodeError
except AttributeError:
    JSONDecodeError = ValueError


def is_not_null_and_blank_str(content):
    """
    非空字符串
    :param content: 字符串
    :return: 非空 - True，空 - False
    """
    if content and content.strip():
        return True
    else:
        return False


class LarkBot(object):

    def __init__(self, webhook, secret=None, pc_slide=False, fail_notice=False):
        '''
        机器人初始化
        :param webhook: 飞书群自定义机器人webhook地址
        :param secret:  机器人安全设置页面勾选“加签”时需要传入的密钥
        :param pc_slide:  消息链接打开方式，默认False为浏览器打开，设置为True时为PC端侧边栏打开
        :param fail_notice:  消息发送失败提醒，默认为False不提醒，开发者可以根据返回的消息发送结果自行判断和处理
        '''
        super(LarkBot, self).__init__()
        self.headers = {'Content-Type': 'application/json; charset=utf-8'}
        print('webhook {}'.format(webhook))
        self.webhook = webhook
        self.secret = secret
        self.pc_slide = pc_slide
        self.fail_notice = fail_notice

    def send_text(self, msg, open_id=[]):
        """
        消息类型为text类型
        :param msg: 消息内容
        :return: 返回消息发送结果
        """
        data = {"msg_type": "text", "at": {}}
        if is_not_null_and_blank_str(msg):    # 传入msg非空
            data["content"] = {"text": msg}
        else:
            logging.error("text类型，消息内容不能为空！")
            raise ValueError("text类型，消息内容不能为空！")

        logging.debug('text类型：%s' % data)
        return self.post(data)

    def post(self, data):
        """
        发送消息（内容UTF-8编码）
        :param data: 消息数据（字典）
        :return: 返回消息发送结果
        """
        try:
            post_data = json.dumps(data)
            response = requests.post(self.webhook, headers=self.headers, data=post_data, verify=False)
        except requests.exceptions.HTTPError as exc:
            logging.error("消息发送失败， HTTP error: %d, reason: %s" % (exc.response.status_code, exc.response.reason))
            raise
        except requests.exceptions.ConnectionError:
            logging.error("消息发送失败，HTTP connection error!")
            raise
        except requests.exceptions.Timeout:
            logging.error("消息发送失败，Timeout error!")
            raise
        except requests.exceptions.RequestException:
            logging.error("消息发送失败, Request Exception!")
            raise
        else:
            try:
                result = response.json()
            except JSONDecodeError:
                logging.error("服务器响应异常，状态码：%s，响应内容：%s" % (response.status_code, response.text))
                return {'errcode': 500, 'errmsg': '服务器响应异常'}
            else:
                logging.debug('发送结果：%s' % result)
                # 消息发送失败提醒（errcode 不为 0，表示消息发送异常），默认不提醒，开发者可以根据返回的消息发送结果自行判断和处理
                if self.fail_notice and result.get('errcode', True):
                    time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    error_data = {
                        "msgtype": "text",
                        "text": {
                            "content": "[注意-自动通知]飞书机器人消息发送失败，时间：%s，原因：%s，请及时跟进，谢谢!" % (
                                time_now, result['errmsg'] if result.get('errmsg', False) else '未知异常')
                        },
                        "at": {
                            "isAtAll": False
                        }
                    }
                    logging.error("消息发送失败，自动通知：%s" % error_data)
                    requests.post(self.webhook, headers=self.headers, data=json.dumps(error_data))
                return result


app = Flask(__name__)
app.debug = False 

def work_time():
    workTime=['10:00:00','19:00:00']
    dayOfWeek = datetime.datetime.now().weekday()
    #dayOfWeek = datetime.today().weekday()
    beginWork=datetime.datetime.now().strftime("%Y-%m-%d")+' '+workTime[0]
    endWork=datetime.datetime.now().strftime("%Y-%m-%d")+' '+workTime[1]
    beginWorkSeconds=time.time()-time.mktime(time.strptime(beginWork, '%Y-%m-%d %H:%M:%S'))
    endWorkSeconds=time.time()-time.mktime(time.strptime(endWork, '%Y-%m-%d %H:%M:%S'))
    if (int(dayOfWeek) in range(5)) and int(beginWorkSeconds)>0 and int(endWorkSeconds)<0:
        return True
    else:
        return False
    
def process_message(text: str):
    """处理消息
    如果非工作时间，不空就直接塞进历史
    如果是工作时间，处理历史，然后看该不该发这条消息

    Args:
        text (str): _description_

    Returns:
        _type_: _description_
    """
    FILENAME = 'history.txt'
    
    if not work_time():
        if text is not None:
            print("=== Not worktime, add {} to history.txt".format(text))
            with open(FILENAME, 'a') as f:
                f.write(text)
        return jsonify(dict(state="ok"))

    if os.path.exists(FILENAME):
        # send history msg if work_time
        text = "历史消息: \n"
        with open(FILENAME, 'r') as f:
            history = f.readlines()
            for item in history:
                text += item
        os.remove(FILENAME)

    if text is not None and len(text) > 0:
        print("=== Send text: {}".format(text))
        bot = LarkBot(lark_webhook())
        bot.send_text(text)
    
    return jsonify(dict(state="ok"))


def left_an_comment(number):
    """发个默认评论 at 领导，在非工作时间。
    不打算再基于 topic 做分析，让管理问题回到管理本身

    Args:
        number (_type_): _description_
    """
    if (number is None):
        print("Oops, input number is None. \n")
        return
    
    url = "https://api.github.com/repos/open-mmlab/mmdeploy/issues/{}/comments".format(number)
    cmd = """curl   -X POST  -H "Accept: application/vnd.github+json"  -H "Authorization: token {}" {}  """.format(github_token(), url) + "-d '{\"body\":\" {} \"}'".format(issue_comment())
    print('=== command {}'.format(cmd))
    os.system(cmd)


@app.route('/github/lark',methods=['post'])
def lark_robot():
    if request.data is None or len(request.data) == 0:
        return jsonify(dict(state="ok"))

    jsonstr = request.data.decode('utf-8') 
    jsonobj = json.loads(jsonstr)
    if jsonobj is None:
        print("parse json object is None: {}".format(jsonstr))
        return jsonify(dict(state="ok"))

    action = None 
    if "action" in jsonobj:
        action = jsonobj['action']

    url = None
    type_ = None
    text = None

    if "issue" in jsonobj and "html_url" in jsonobj['issue']:
        issue = jsonobj['issue']

        if action == 'opened':
            type_ = "issue_open"
            title = ""
            url = ""
            if 'title' in issue:
                title = issue['title']
            if 'html_url' in issue:
                url = issue['html_url']

            text = "[新的 issue] 标题: {}, 链接 {} \n".format(title, url)

            if not work_time() and text is not None:
                # open an issue during non work time, at lvhan
                left_an_comment(issue['number'])
        elif action == 'assigned':
            if 'sender' in jsonobj and 'assignee' in jsonobj:
                _from = jsonobj['sender']['login']
                _to = jsonobj['assignee']['login']
                title = issue['title']
                url = issue['html_url']

                if _from != _to:
                    type_ = 'issue_other_assign'
                    text = "[assign issue] 标题: {}, 链接 {} @{} \n".format(title, url, _to)
            

    elif "pull_request" in jsonobj and "requested_reviewer" in jsonobj and action != "review_request_removed":
        type_ = "pull_request_open"
        url = jsonobj['pull_request']['html_url']

        reviewer = "" 
        req = jsonobj['requested_reviewer']
        if 'login' in req:
            reviewer += req['login']

        text = "请求 {} review PR, 链接 {} \n".format(reviewer, url)

    print("=== Got type: {} | url: {} | action {}".format(type_, url, action))
    
    return process_message(text)
    # return jsonify(dict(state="ok"))
    

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=50000)
