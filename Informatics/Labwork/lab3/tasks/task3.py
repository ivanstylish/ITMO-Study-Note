import re
import json

def find_specific_words(s: str, letters: str, distance: int):
    pattern = r'^[^' + letters + r']*' + letters[0] + r'[^' + letters + r']{' + str(distance) + r'}' + letters[1] + r'[^' + letters + r']{' + str(distance) + r'}' + letters[2] + r'[^' + letters + r']*$'
    matches = re.fullmatch(pattern, s) # 查看整个字符串
    return matches

string = input("Enter a string: ")

test = list(string.split(',')) # 将用户输入的字符串按逗号分割成一个列表

# 第一部分是距离расстояние: ,从第十一位开始是数字
# 第二部分是字母Символы: ,从第十位开始是所选字母
# 第三部分是字符串Текст: ,从第六位开始是文本
distance = int(test[0][11:])
# 获取字母和距离
letters = test[1][10:]
# 获取要处理的文本
s = list(test[2][6:].split(' '))

ans = ''
for i in s:
    if find_specific_words(i, letters, distance) is not None: # 用函数判断是否符合条件
        ans += i + ' ' # 如果匹配成功，将该单词添加到 ans 字符串中，并用空格分隔。

# 移除末尾多余的空格
ans = ans.strip()

my_json = {'answers': [ans]}

with open('result.json', 'w', encoding="utf-8") as file:
    dumped_json = json.dumps(my_json, ensure_ascii=False)
    file.write(dumped_json)

print("Found words: ", ans)


