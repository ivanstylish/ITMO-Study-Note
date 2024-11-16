import re
import json

def find_duplicated_words(string):
    pattern = r'\b(\w+)\s+\1\b'
    return re.sub(pattern, r'\1',string)

string = input("Enter a string: ")
my_ans = find_duplicated_words(string)
my_json = {} # 分配内存空间
my_json["answers"] = [my_ans]

with open('result.json', 'w', encoding="utf-8") as file:
    dumped_json = json.dumps(my_json, ensure_ascii=False)
    file.write(dumped_json)

print(my_ans)