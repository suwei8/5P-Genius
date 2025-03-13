import pandas as pd
import numpy as np
import os
import requests
import json
from datetime import datetime
from zoneinfo import ZoneInfo

# 定义北京时间时区
beijing_timezone = ZoneInfo("Asia/Shanghai")
now = datetime.now(beijing_timezone)

file_path = 'lottery_data.csv'

def analyze_and_predict_lottery_data(file_path):
    try:
        data = pd.read_csv(file_path)
    except Exception as e:
        raise Exception(f"文件读取错误: {e}")

    try:
        data['开奖日期'] = pd.to_datetime(data['开奖日期']).dt.tz_localize('Asia/Shanghai')
    except Exception as e:
        raise Exception(f"解析开奖日期错误: {e}")

    try:
        data['开奖号码'] = data['开奖号码'].apply(lambda x: list(map(int, x.split(','))))
    except Exception as e:
        raise Exception(f"解析开奖号码错误: {e}")

    data.sort_values('期号', inplace=True)

    # 获取最近5期的开奖号码
    last_5_draws = data.tail(5)

    # 获取所有可能的数字 (假设数字范围是0-9)
    all_possible_numbers = set(range(10))

    # 按位置统计频率
    position_freqs = {i: {} for i in range(5)}  # 5个位置
    for _, row in last_5_draws.iterrows():
        for i, num in enumerate(row['开奖号码']):
            if num not in position_freqs[i]:
                position_freqs[i][num] = 0
            position_freqs[i][num] += 1

    # 预测号码：优先选择未出现过的数字
    lowest_freq_numbers = []
    for i in range(5):
        appeared_numbers = set(position_freqs[i].keys())
        # 找到未出现的数字
        missing_numbers = all_possible_numbers - appeared_numbers

        if missing_numbers:  # 如果有未出现的数字，则优先选择它们
            # 从未出现的数字中随机选一个
            predicted_number = np.random.choice(list(missing_numbers))
        else:
            # 否则选择频率最低的数字
            sorted_freq = sorted(position_freqs[i].items(), key=lambda x: x[1])
            predicted_number = sorted_freq[0][0]  # 频率最低的数字

        lowest_freq_numbers.append(predicted_number)

    # 保留原有的预测逻辑
    all_numbers = [num for nums in data['开奖号码'] for num in nums]
    last_30_numbers = [num for nums in data['开奖号码'][-30:] for num in nums]

    overall_freq = pd.Series(all_numbers).value_counts(normalize=True).sort_values(ascending=False).reset_index()
    overall_freq.columns = ['号码', '频率']
    recent_freq = pd.Series(last_30_numbers).value_counts(normalize=True).sort_values(ascending=False).reset_index()
    recent_freq.columns = ['号码', '频率']

    # 预测号码（5个数字）
    predicted_numbers = []
    for position in range(5):
        weights = overall_freq['频率'] + recent_freq['频率']
        weights /= weights.sum()
        predicted_number = np.random.choice(range(10), p=weights)
        predicted_numbers.append(predicted_number)

    latest_draw = data.iloc[-1]
    latest_draw_numbers = latest_draw['开奖号码']
    latest_draw_info = f"{','.join(map(str, latest_draw_numbers))}"

    data['对子'] = data['开奖号码'].apply(lambda x: len(set(x)) == 2)
    pair_draws = data[data['对子']].sort_values('开奖日期')

    if not pair_draws.empty:
        latest_pair_draw = pair_draws.iloc[-1]
        days_since_pair = (now - latest_pair_draw['开奖日期']).days
        latest_pair_draw_numbers = latest_pair_draw['开奖号码']
    else:
        days_since_pair = "无记录"
        latest_pair_draw_numbers = "无记录"

    return {
        'predicted_numbers': predicted_numbers,
        'lowest_freq_numbers': lowest_freq_numbers,
        'latest_draw_info': latest_draw_info,
        'latest_draw_numbers': latest_draw_numbers,
        'days_since_pair': days_since_pair,
        'latest_pair_draw_numbers': latest_pair_draw_numbers
    }

result = analyze_and_predict_lottery_data(file_path)

import time

if __name__ == "__main__":
    try:
        results = analyze_and_predict_lottery_data(file_path)
        today_date = now.strftime('%Y-%m-%d')
        url = "http://140.238.6.167:5001/send_template"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": "sw63828"
        }
        to_users = [
            "oXUv66MibUi7VInLBf7AHqMIY438",
            "oXUv66DvDIoQG39Vnspwj97QVLn4"
        ]
        template_id = "895d_IyG9jyQDDKVNomDrEG3m6U5dtPA9wJXAJzewek"  # 去掉逗号，确保是字符串
        common_data = {
            "data": {
                "character_string1":  ','.join(map(str, result['predicted_numbers'])),
                "thing6": ','.join(map(str, result['lowest_freq_numbers'])),
                "thing2": "昨天:" + result['latest_draw_info'],
                "thing7": f"已{result['days_since_pair']}天-{','.join(map(str, result['latest_pair_draw_numbers']))}",
                "time8": now.strftime('%Y-%m-%d %H:%M:%S'),
                "remark": "点击查看详情",
            },
            "url": "https://3d.13982.com/"
        }

        for user_id in to_users:
            data = {
                "to_user": user_id,
                "template_id": template_id,  # 确保在请求体中包含 template_id
                **common_data
            }

            # 重试机制
            retries = 10  # 设置最大重试次数
            for attempt in range(retries):
                response = requests.post(url, headers=headers, data=json.dumps(data))
                if response.status_code == 200:
                    print(f"消息成功发送给用户 {user_id}")
                    break  # 成功则跳出重试循环
                else:
                    print(f"HTTP错误 {response.status_code} 发送给用户 {user_id}: {response.text}")
                    if attempt < retries - 1:
                        print("等待 5 秒后重试...")
                        time.sleep(5)  # 等待5秒后重试
                    else:
                        print(f"发送失败，已达到最大重试次数 {retries} 次")

    except Exception as e:
        print(f"运行脚本时出错: {e}")
