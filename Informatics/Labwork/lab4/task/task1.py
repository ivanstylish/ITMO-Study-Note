import time
def parse_xml_to_yaml(input_file, output_file):
    """
    将任意 XML 文件解析为 YAML 格式并输出
    """
    with open(input_file, 'r', encoding='utf-8') as infile:
        xml_data = infile.read().strip()

    parsed_data = parse_xml(xml_data)

    yaml_data = dict_to_yaml(parsed_data)

    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(yaml_data)

    print(f"Succesfully print out: {output_file}")


def parse_xml(data):
    """
    递归解析 XML 数据为嵌套字典或列表，支持重复标签
    """
    result = {}
    while '<' in data:
        start_tag = data.find('<')
        end_tag = data.find('>', start_tag)
        if start_tag == -1 and end_tag == -1:
            break

        key = data[start_tag+1:end_tag].split(" ")[0].strip("/")
        closing_tag = f"</{key}>"

        if closing_tag in data:
            content_start = end_tag + 1
            content_end = data.find(closing_tag)
            content = data[content_start:content_end].strip()
            data = data[content_end + len(closing_tag):].strip()

            parsed_data = parse_xml(content) if "<" in content else content
            # 若包含xml标签则递归解析该内容；若不包含则直接返回该内容

            if key in result:
                if not isinstance(result[key], list):
                    result[key] = [result[key]]
                result[key].append(parsed_data)
            else:
                result[key] = parsed_data
        else:
            data = data[end_tag + 1:]
    return result

def dict_to_yaml(data, indent=0):
    """
    简单递归将字典转换为 YAML 格式字符串
    """
    yaml = []
    for key, value in data.items():
        if isinstance(value, dict): # 检查是否为字典类型
            yaml.append(f"{' ' * indent}{key}:")
            yaml.append(dict_to_yaml(value, indent + 2))
        elif isinstance(value, list): # 检查如果是列表类型的话
            yaml.append(f"{' ' * indent}{key}:")
            for item in value:
                if isinstance(item, dict):
                    yaml.append(f"{' ' * (indent + 2)}-")
                    yaml.append(dict_to_yaml(item, indent + 4))
                else:
                    yaml.append(f"{' ' * (indent + 2)}- {item}")
        else:
            yaml.append(f"{' ' * indent}{key}: {value}")
    return "\n".join(yaml)

if __name__ == "__main__":
    input_file = "../myXML/input_schedule.xml"
    output_file = "../myYAML/output_schedule.yaml"
    start_time = time.time()
    parse_xml_to_yaml(input_file, output_file)
    end_time = time.time()
    print(f"Parsing took {end_time - start_time}")
