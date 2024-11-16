import re
import json

cron_check = re.compile(
    r"^([0-5]?\d|\*|(\*/[1-5]?\d))\s"  # 分钟
    r"([0-1]?\d|2[0-3]|\*|(\*/[1-9]|1[0-9]|2[0-3]))\s"  # 小时
    r"([0-9]|[1-2]\d|3[0-1]|\*|(\*/[1-9]|[1-2]\d|3[0-1]))\s"  # 月份的一天
    r"(\d|1[0-2]|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|\*)\s"  # 月份
    r"([0-6]|sun|mon|tue|wed|thu|fri|sat|\*|(\*/[0-6]))$"  # 周内某天
)


def cron_test(expressions):
    for expr in expressions:
        match = cron_check.match(expr)
        result = {
            "expression": expr,
            "vaild": bool(match)  # 检查是否有效
        }
        my_ans.append(result)


exp = input("Enter regular expression: ")
my_json = {}
my_ans = []
my_json["ans"] = my_ans


with open('result.json', 'w', encoding="utf-8") as file:
    dumped_json = json.dumps(my_json, ensure_ascii=False)
    file.write(dumped_json)
