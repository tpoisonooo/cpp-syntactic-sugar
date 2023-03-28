# coding=UTF-8
import requests
import json

def login():
    headers = {
       "Content-Type": "application/json" 
    }
    data = {
        'account': '',
        'password': ''
    }

    resp = requests.post('http://114.107.252.79:9899/member/login', data=json.dumps(data), headers = headers)
    print(resp, resp.content)
    if resp.status_code == 200:
        x = json.loads(resp.content)
        return x['data']['Authorization']
    else:
        return None

def ipadLogin(auth):
# {
#     "code": "1000",
#     "message": "处理成功",
#     "data": {
#         "wId": "4d83b7b9-e218-4bc9-bd2f-5eb08b904cd9",
#         "qrCodeUrl": "http://wxapii.oos-sccd.ctyunapi.cn/20230327/7c6c7681-b993-47ff-ac30-b82d56e96bae_qrcode.png?AWSAccessKeyId=9e882e7187c38b431303&Expires=1680513972&Signature=Wxd4Ss1szgjQLqX%2BLRkQnEH%2FHTw%3D"
#     }
# }
    headers = {
       "Content-Type": "application/json",
       "Authorization": auth
    }
    data = {
        "wcId": "",
        "proxy": 3
    }

    resp = requests.post('http://114.107.252.79:9899/iPadLogin', data=json.dumps(data), headers = headers)
    print(resp, resp.content)
    if resp.status_code == 200:
        x = json.loads(resp.content)['data']
        
        if x is None:
            with open('record.txt') as f:
                x = json.load(f)
                return x['wId'], x['qrCodeUrl']
        else:
            with open('record.txt', 'w') as f:
                json.dump(x, f)
                return x['wId'], x['qrCodeUrl']
    else:
        return None, None


def getLoginInfo(auth, wid):
# {
#     "code": "1000",
#     "message": "处理成功",
#     "data": {
#         "deviceType": null,
#         "country": "CN",
#         "wAccount": null,
#         "city": "",
#         "newDevice": 1,
#         "signature": null,
#         "nickName": "焕军",
#         "sex": 0,
#         "headUrl": "https://wx.qlogo.cn/mmhead/ver_1/pXusgSmhNGw4yoK3Ne0Go6OVwhd578oXhjGhODzPaJNKaYdEDx4gUEWIzez1R5QyCgevy50I3rdyTiay43byMznXlyyOGNDUSAdOCvZFPY2Q/0",
#         "type": 1,
#         "smallHeadImgUrl": "https://wx.qlogo.cn/mmhead/ver_1/pXusgSmhNGw4yoK3Ne0Go6OVwhd578oXhjGhODzPaJNKaYdEDx4gUEWIzez1R5QyCgevy50I3rdyTiay43byMznXlyyOGNDUSAdOCvZFPY2Q/132",
#         "wcId": "wxid_39qg5wnae8dl12",
#         "wId": "52342b1c-3291-4b9f-bbbd-57a0db099504",
#         "mobilePhone": "13122360295",
#         "uin": null,
#         "status": 3,
#         "username": "18612393510"
#     }
# }
    headers = {
       "Content-Type": "application/json",
       "Authorization": auth
    }
    data = {
        "wId": wid
    }

    resp = requests.post('http://114.107.252.79:9899/getIPadLoginInfo', data=json.dumps(data), headers = headers)
    print(resp, resp.content)
    if resp.status_code == 200:
        x = json.loads(resp.content)['data']
        with open('me.txt', 'w') as f:
            json.dump(x, f)
        return x['wcId']
    else:
        return None, None


def setCallback(auth, wid):
    headers = {
       "Content-Type": "application/json",
       "Authorization": auth
    }
    data = {
        "httpUrl": "http://139.196.49.6:5000/callback",
        "type": 2
    }

    resp = requests.post('http://114.107.252.79:9899/setHttpCallbackUrl', data=json.dumps(data), headers = headers)
    print(resp, resp.content)
    if resp.status_code == 200:
        return True
    return False


def initAddrList(auth, wid):
    headers = {
       "Content-Type": "application/json",
       "Authorization": auth
    }
    data = {
        "wId": wid
    }

    resp = requests.post('http://114.107.252.79:9899/getAddressList', data=json.dumps(data), headers = headers)
    print(resp, resp.content)
    if resp.status_code == 200:
        return True
    return False


auth = login()
with open('auth.txt', 'w') as f:
    f.write(auth)

if auth != None:
    wid, qrcode = ipadLogin(auth)

    print(wid)
    print('=' * 20)
    print(qrcode)
    print('=' * 20)
    wcid = getLoginInfo(auth, wid)
    setCallback(auth, wid)

    initAddrList(auth, wid)
