import pandas as pd

# 1. 读取lottery_data.csv文件
df = pd.read_csv('lottery_data.csv')

# 2. 定义一个函数来提取"开奖号码"字段的前3个数字并计算结果
def calculate_result(row, multiplier):
    # 提取"开奖号码"字段前3个数字，并将其转换为整数
    numbers = row['开奖号码'].split(',')
    first_three_digits = int(numbers[0] + numbers[1] + numbers[2])  # 拼接前三个数字
    return round(first_three_digits * multiplier, 3)  # 计算乘积并保留三位小数

# 3. 在lottery_data.csv中增加新列"0.238结果"，并计算该列的值
df['0.238结果'] = df.apply(lambda row: calculate_result(row, 0.238), axis=1)

# 4. 在lottery_data.csv中增加新列"0.236结果"，并计算该列的值
df['0.236结果'] = df.apply(lambda row: calculate_result(row, 0.236), axis=1)

# 5. 在lottery_data.csv中增加新列"0.206结果"，并计算该列的值
df['0.206结果'] = df.apply(lambda row: calculate_result(row, 0.206), axis=1)

# 6. 将修改后的DataFrame保存为take_lottery_data.csv
df.to_csv('take_lottery_data.csv', index=False)

print("更新完成，已保存为take_lottery_data.csv")
