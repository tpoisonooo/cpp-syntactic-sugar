# -*- coding:utf-8 -*-
from xmlrpc.client import Boolean
from flask import Flask, request, jsonify
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


def issue_timeline(id):
    """获取一个 issue 的 timeline

    Args:
        id (_type_): _description_

    Returns:
        _type_: _description_
    """
    TIMELINE_FILE = "timeline.json"
    
    url = "https://api.github.com/repos/open-mmlab/mmdeploy/issues/{}/timeline".format(id)
    cmd = 'curl -H "Accept: application/vnd.github+json"  -H "Authorization: token <TOKEN> {}"  > {}'.format(url,  TIMELINE_FILE)
    os.system(cmd)
    
    if not os.path.exists(TIMELINE_FILE):
        print("Ooops, get detail issue failed, pls check API or net.\n")
        return None
        
    detail = None
    with open(TIMELINE_FILE) as f:
        detail = json.load(f)
        
    os.remove(TIMELINE_FILE)
    return detail


def all_pr():
    PR_FILE = "pr.json"
    url = 'curl -H "Accept: application/vnd.github+json"  -H "Authorization: token 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"  https://api.github.com/repos/open-mmlab/mmdeploy/pulls > {}'.format(PR_FILE)
    os.system(url)
    
    if not os.path.exists(PR_FILE):
        print("Ooops, get all pr failed, pls check API or net.\n")
        return None
        
    pr = None
    with open(PR_FILE) as f:
        pr = json.load(f)
        
    os.remove(PR_FILE)
    return pr


class Memo(object):
    def __init__(self, filename) -> None:
        self.FILENAME = filename
        
    def is_notified(self, number) -> Boolean:
        
        if not os.path.exists(self.FILENAME):
            return False
        
        with open(self.FILENAME) as f:
            lines = f.readlines()
            for line in lines:
                if number == int(line):
                    return True
        return False
    
    def mark_as_notified(self, number):
        with open(self.FILENAME, 'a') as f:
            f.write(str(number) + '\n')


def outdate(input: str, _days):
    """判断输入的时间戳加 _days 是否过期

    Args:
        input (str): UTC 时间戳，例如  2022-08-12T09:09:27Z
        _days (_type_): _description_

    Returns:
        _type_: _description_
    """

    year = int(input[0:4])
    month = int(input[5:7])
    day = int(input[8:10])
    hour = int(input[11:13])
    min = int(input[14:16])
    sec = int(input[17:19])
    
    dt = datetime.datetime(year, month, day, hour, min, sec)
    dt = dt + datetime.timedelta(days=_days)
    dt = dt - datetime.timedelta(hours=68)
    
    now = datetime.datetime.now()
    return now > dt


def pr_notify(days):
    """
        催处理 PR 超过 5 天的 PR，只催一次
        
    Args:
        days (_type_): _description_ 多少天
    """
    prs = all_pr()
    review_list = []
    request_list = []
    if prs is None:
        print("Oops, we got an weired prs, pls check")
        return

    memo = Memo('pr_notified.txt')
    for pr in prs:
        if 'state' not in pr or 'created_at' not in pr:
            print("Oops, we got an weired pr {}".format(pr))
            continue
            
        if pr['state'] != 'open':
            continue
        
        if outdate(pr['created_at'], days) and not memo.is_notified(pr['number']):
            reviewer_text = ""
            if len(pr['requested_reviewers']) > 0:
                for reviewer in pr['requested_reviewers']:
                    reviewer_text = reviewer_text + " " +  reviewer['login']
                review_list.append(pr['html_url'] + " ," + reviewer_text)
            else:
                request_list.append(pr['html_url'])
            
            memo.mark_as_notified(pr['number'])
            
    # proc result
    text = "" 
    if len(review_list) > 0:
        text = "以下 PR 需要 reviewer 处理：\n"
        for item in review_list:
            text = text + item + "\n"
        
        text = text + "\n"
    
    if len(request_list) > 0:
        text = text + "以下 PR 还没有 reviewer：\n"
        for item in request_list:
            text = text + item + "\n"
        
    if len(text) > 0:
        print("=== append PR to history {}".format(text))
        with open('history.txt', 'a') as f:
            f.write(text)


if __name__ == "__main__":
    # 每隔 1 小时扫一次
    while(True):
        pr_notify(7)
        time.sleep(3600)
