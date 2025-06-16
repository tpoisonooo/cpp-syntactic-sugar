import json
from typing import List
from datetime import datetime
import requests
import os
from loguru import logger

class BaseNotifier:
    async def execute(self, messages: List[str]):
        raise NotImplementedError("Subclasses should implement this method")

def ymd():
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    return f"{year:04d}-{month:02d}-{day:02d}"

class WeChat(BaseNotifier):
    def __init__(self):
        config = '/root/HuixiangDou/wkteam/license.json'
        with open(config) as f:
            data = json.load(f)
            self.wId = data['wId']
            self.auth = data['auth']
        self.WKTEAM_IP_PORT = '121.229.29.88:9899'

    def post(self, url, data, headers):
        """Wrap http post and error handling."""
        resp = requests.post(url, data=json.dumps(data), headers=headers)
        json_str = resp.content.decode('utf8')
        logger.debug(json_str)
        if resp.status_code != 200:
            return None, Exception('wkteam auth fail {}'.format(json_str))
        json_obj = json.loads(json_str)
        if json_obj['code'] != '1000':
            return json_obj, Exception(json_str)

        return json_obj, None

    def send_message(self, text: str, groupId = '18356748488@chatroom'):
        """Send a message to WeChat group."""
        send_log = 'logs/wechat_send_{}.log'.format(ymd())
        if os.path.exists(send_log):
            return

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.auth
        }
        data = {'wId': self.wId, 'wcId': groupId, 'content': text}

        json_obj, err = self.post(url='http://{}/sendText'.format(
            self.WKTEAM_IP_PORT),
                                  data=data,
                                  headers=headers)
        if err is not None:
            return err

        sent = json_obj['data']
        sent['wId'] = self.wId
        sent['msg'] = text

        with open(send_log, 'a') as f:
            f.write(json.dumps(sent, ensure_ascii=False) + '\n')
        return None

    async def execute(self, messages: List[str]):
        """Send a message to WeChat group."""
        for message in messages:
            if not message:
                continue
            self.send_message(message)
