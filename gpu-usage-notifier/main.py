import requests
import time
import datetime
import pynvml  # 需要安装 pynvml 库，用于获取 GPU 信息
from lark import LarkBot

# 飞书 Webhook 地址
FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/5fc2f605-c583-4db3-92b8-da55a*******"

# 配置参数
CHECK_INTERVAL = 3600  # 检查间隔（秒）
EMPTY_THRESHOLD = 25  # 显存使用率低于此值视为“空闲”
EMPTY_HOURS = 6  # 连续空闲次数
MAX_DAILY_MESSAGES = 1  # 每天最多发送消息次数

# 初始化变量
gpu_empty_hours = {}  # 记录每个 GPU 的连续空闲小时数
daily_message_count = 0
last_message_date = None


def send_feishu_message(messages):
    content = f'[H800] 当前有 {len(messages)} 块空闲'
    print('---')
    print(content)
    print('---')
    
    bot = LarkBot(webhook='https://open.feishu.cn/open-apis/bot/v2/hook/5fc2f605-c583-4db3-92b8-da55a*******')
    bot.send_text(msg=content)


def check_gpu_usage():
    """检查每个 GPU 的使用情况"""
    pynvml.nvmlInit()
    device_count = pynvml.nvmlDeviceGetCount()
    gpu_usage = {}

    for i in range(device_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        total_memory = mem_info.total
        used_memory = mem_info.used
        usage_rate = (used_memory / total_memory) * 100 if total_memory > 0 else 0
        gpu_usage[i] = usage_rate

    pynvml.nvmlShutdown()
    return gpu_usage

def work_time():
    workTime=['9:00:00','21:00:00']
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

def main():
    global daily_message_count, last_message_date

    while True:
        current_time = datetime.datetime.now()

        print(f"检查时间：{current_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # 检查每个 GPU 的使用情况
        gpu_usages = check_gpu_usage()
        send_message = []
        for gpu_id, usage_rate in gpu_usages.items():
            print(f"GPU {gpu_id} 显存使用率：{usage_rate:.2f}%")

            if usage_rate < EMPTY_THRESHOLD:
                if gpu_id not in gpu_empty_hours:
                    gpu_empty_hours[gpu_id] = 0
                gpu_empty_hours[gpu_id] += 1
                print(f"GPU {gpu_id} 连续空闲小时数：{gpu_empty_hours[gpu_id]}")
            else:
                gpu_empty_hours[gpu_id] = 0

            # 检查是否满足发送提醒的条件
            if gpu_empty_hours[gpu_id] >= EMPTY_HOURS:
                today = current_time.date()
                if last_message_date != today and daily_message_count < MAX_DAILY_MESSAGES:
                    send_message.append(f"GPU {gpu_id} 已连续空闲 {EMPTY_HOURS} 小时！当前显存使用率：{usage_rate:.2f}% \n")
                else:
                    print(f"GPU {gpu_id} 已达到空闲条件，但今日消息已发送，不再重复发送")

        if send_message:
            daily_message_count += 1
            send_feishu_message(send_message)
            last_message_date = today
            
        # 等待下一个检查周期
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
