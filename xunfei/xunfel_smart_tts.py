#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""讯飞超拟人语音合成（super smart TTS）调用封装

概述
----
讯飞"超拟人语音合成"是一个 WebSocket 流式接口：建立连接后发送一次文本，
服务端流式返回 base64 编码的音频帧，收齐后拼接即为完整音频文件。
本模块将其封装为同步函数，对外表现与"离线合成出 mp3 文件"一致。

- 接口文档: https://www.xfyun.cn/doc/spark/super%20smart-tts.html
- 接口地址: wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/mcd9m97e6
- 鉴权方式: HMAC-SHA256 签名（见 _auth_url），与讯飞其他 WebSocket 接口相同
- 文本上限: 单次会话总文本不超过 64K 字节
- 音频格式: encoding="lame" 即 mp3（24kHz 单声道），也可选 raw(pcm) 等

依赖
----
    pip install websockets

已验证可用（该账号已开通）的发音人 vcn
--------------------------------------
    x6_lingxiaoxuan_pro  聆小璇      x6_lingfeiyi_pro     聆飞逸
    x6_lingxiaoyue_pro   聆小玥      x6_lingyuyan_pro     聆玉言
    x6_lingxiaoshan_pro  聆小珊      x6_lingyufei_pro     聆玉菲
    x6_feizheChat_pro    聆飞哲
注意：发音人权限与服务量是两个独立授权，使用未开通的发音人会返回错误码 11200。
完整发音人列表见接口文档"发音人列表"一节。

用法
----
    from xunfel_smart_tts import synthesize_to_mp3
    synthesize_to_mp3("要合成的文本", "output.mp3")                     # 默认发音人
    synthesize_to_mp3("要合成的文本", "output.mp3", vcn="x6_lingfeiyi_pro")

错误码: 0 成功；11200 功能/发音人未授权；10163 参数校验失败（message 含原因）；
其余见接口文档"错误码"一节。
"""

import asyncio
import base64
import hashlib
import hmac
import json
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

import websockets

# ===== 账号凭证（讯飞控制台-超拟人语音合成服务页获取）=====

# ===== 接口常量 =====
HOST = "cbm01.cn-huabei-1.xf-yun.com"
PATH = "/v1/private/mcd9m97e6"
WS_URL = f"wss://{HOST}{PATH}"

# 默认发音人（已验证该账号可用）
DEFAULT_VCN = "x6_lingxiaoxuan_pro"

# 该账号已开通的发音人
AVAILABLE_VCN = [
    "x6_lingxiaoxuan_pro", "x6_lingfeiyi_pro", "x6_lingxiaoyue_pro",
    "x6_lingyuyan_pro", "x6_lingxiaoshan_pro", "x6_lingyufei_pro",
    "x6_feizheChat_pro"
]


def _auth_url():
    """生成带 HMAC-SHA256 鉴权参数的 WebSocket URL（签名细节见接口文档）。"""
    date = format_date_time(mktime(datetime.now().timetuple()))
    sig_origin = f"host: {HOST}\ndate: {date}\nGET {PATH} HTTP/1.1"
    sig = base64.b64encode(
        hmac.new(API_SECRET.encode(), sig_origin.encode(), digestmod=hashlib.sha256).digest()
    ).decode()
    auth_origin = (
        'api_key="%s", algorithm="hmac-sha256", '
        'headers="host date request-line", signature="%s"' % (API_KEY, sig)
    )
    authorization = base64.b64encode(auth_origin.encode()).decode()
    params = {"host": HOST, "date": date, "authorization": authorization}
    return WS_URL + "?" + urlencode(params)


def _build_request(text, vcn, speed, volume, pitch):
    return {
        "header": {"app_id": APP_ID, "status": 2},  # 一次性合成，status 固定 2
        "parameter": {
            "oral": {"oral_level": "mid"},  # 口语化等级: high/mid/low
            "tts": {
                "vcn": vcn,
                "speed": speed, "volume": volume, "pitch": pitch,  # 0-100
                "bgs": 0, "reg": 0, "rdn": 0, "rhy": 0,
                "audio": {
                    "encoding": "lame",      # lame = mp3
                    "sample_rate": 24000,
                    "channels": 1,
                    "bit_depth": 16,
                    "frame_size": 0,
                },
            },
        },
        "payload": {
            "text": {
                "encoding": "utf8",
                "compress": "raw",
                "format": "plain",
                "status": 2,
                "seq": 0,
                "text": base64.b64encode(text.encode("utf-8")).decode(),
            }
        },
    }


async def _synthesize(text, vcn, speed, volume, pitch):
    """发起一次合成会话，返回拼接好的 mp3 字节。失败抛 RuntimeError。"""
    audio = b""
    async with websockets.connect(_auth_url()) as ws:
        await ws.send(json.dumps(_build_request(text, vcn, speed, volume, pitch)))
        async for raw in ws:
            msg = json.loads(raw)
            header = msg.get("header", {})
            code = header.get("code")
            if code != 0:
                raise RuntimeError(
                    "合成失败 code=%s message=%s sid=%s"
                    % (code, header.get("message"), header.get("sid"))
                )
            payload = msg.get("payload") or {}
            audio_seg = payload.get("audio") or {}
            if audio_seg.get("audio"):
                audio += base64.b64decode(audio_seg["audio"])
            if audio_seg.get("status") == 2:  # status=2 表示音频流结束
                break
    return audio


def synthesize_to_mp3(text, output_mp3, vcn=DEFAULT_VCN, speed=50, volume=50, pitch=50):
    """把 text 合成为 mp3 并写入 output_mp3，返回输出文件路径。

    text 总字节数（utf-8）不能超过 64K。失败抛 RuntimeError（含讯飞错误码与 sid）。
    """
    audio = asyncio.run(_synthesize(text, vcn, speed, volume, pitch))
    with open(output_mp3, "wb") as f:
        f.write(audio)
    return output_mp3


if __name__ == "__main__":
    out = synthesize_to_mp3("你好，这是讯飞超拟人语音合成的测试。", "xunfel_smart_tts_demo.mp3")
    print("生成成功:", out)
