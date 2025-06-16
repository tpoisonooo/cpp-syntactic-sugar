import asyncio
import aiohttp
import json
from datetime import datetime
import json
import numpy as np
import matplotlib.pyplot as plt
from loguru import logger
import os

# 基础任务类
class BaseTask:
    async def execute(self):
        raise NotImplementedError("Subclasses should implement this method")


# {"msg":"操作成功","code":200,"data":[{"ticker":"IXIC","date":"2024-06-12","open":17490.6426,"high":17725.3906,"low":17490.6426,"close":17608.4355,"volume":4976681000.0000},{"ticker":"IXIC","date":"2024-06-13","open":17566.3184,"high":17741.7988,"low":17566.3184,"close":17667.5605,"volume":4446744000.0000},{"ticker":"IXIC","date":"2024-06-14","open":17621.1992,"high":17693.4316,"low":17590.8008,"close":17688.8828,"volume":4563084000.0000},{"ticker":"IXIC","date":"2024-06-17","open":17697.3008,"high":17935.9844,"low":17636.3594,"close":17857.0195,"volume":5611243000.0000},{"ticker":"IXIC","date":"2024-06-18","open":17856.8008,"high":17890.5176,"low":17796.8789,"close":17862.2324,"volume":5434921000.0000},{"ticker":"IXIC","date":"2024-06-20","open":17856.8008,"high":17936.7930,"low":17650.6953,"close":17721.5879,"volume":5742705000.0000},{"ticker":"IXIC","date":"2024-06-21","open":17681.0000,"high":17787.3359,"low":17620.5684,"close":17689.3613,"volume":8658480000.0000},{"ticker":"IXIC","date":"2024-06-24","open":17640.3008,"high":17730.1191,"low":17494.0176,"close":17496.8164,"volume":4944949000.0000},{"ticker":"IXIC","date":"2024-06-25","open":17572.1992,"high":17734.3438,"low":17546.6328,"close":17717.6543,"volume":4444475000.0000},{"ticker":"IXIC","date":"2024-06-26","open":17687.0664,"high":17813.5488,"low":17687.0664,"close":17805.1563,"volume":4883351000.0000}]}
# 监控纳指

class IXICTask(BaseTask):

    def analyze_data(self, data):
        # 解析数据并进行分析
        jsonobj = json.loads(data)
        if jsonobj.get("code") != 200:
            raise Exception(f"Error fetching data: {jsonobj.get('msg', 'Unknown error')}")
        
        # 按日期上升
        records = jsonobj.get("data", [])[::-1]
        prices = []
        close_prices = []
        # 取近三天的
        for record in records[-3:]:
            date = record.get("date")
            open_price = record.get("open")
            close_price = record.get("close")
            prices.append(open_price)
            prices.append(close_price)
            close_prices.append(close_price)

        length = len(prices)
        xvalues = [i for i in range(length)]

        coefficients = np.polyfit(np.array(xvalues), np.array(prices), 1)  # 返回拟合系数 [a, b]

        # 提取拟合系数
        a, b = coefficients

        # 打印拟合结果
        logger.info(f"拟合的直线方程为: y = {a:.2f}x + {b:.2f}")

        # 绘制原始数据点（真实点）
        plt.scatter(xvalues, prices, color='blue', label='real', zorder=5)  # zorder 确保散点在最上层

        # 绘制拟合直线
        x_fit = np.linspace(min(xvalues), max(xvalues), 100)  # 生成用于绘制拟合直线的 x 值
        y_fit = a * x_fit + b  # 计算对应的 y 值
        plt.plot(x_fit, y_fit, color='red', label='sim', linewidth=2)

        # 添加图例和标题
        plt.legend()
        plt.title("sim 3days")
        plt.xlabel("x")
        plt.ylabel("y")

        # 保存图像为 jpg 格式
        if not os.path.exists("imgs"):
            os.makedirs("imgs")
        plt.savefig(os.path.join("imgs", f"IXIC.jpg"), format="jpg", dpi=75)  # 指定保存路径和格式

        if a > 0.1 and close_prices[-1] > close_prices[-2] > close_prices[-3]:
            return f"[三连涨]，近期收盘价格 {close_prices}", None
        elif a < -0.1 and close_prices[-1] < close_prices[-2] < close_prices[-3]:
            return f"[三连跌]，近期收盘价格 {close_prices}", None
        else:
            return None, None

    async def execute(self):
        url = "https://tsanghi.com/api/fin/index/USA/daily?token=demo&ticker=IXIC&order=2"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.text()
                    with open('logs/tsanghi.log', 'a') as log_file:
                        log_file.write(f"{datetime.now()} - Fetched data: {data}\n")
                    return self.analyze_data(data)
                else:
                    return None, f"Failed to fetch data, status code: {response.status}"
