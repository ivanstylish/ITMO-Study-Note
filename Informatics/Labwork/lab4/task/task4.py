import xml.etree.ElementTree as ET
import yaml
import time

def parse_schedule_xml_to_yaml(input_file, output_file):
    tree = ET.parse(input_file)
    root = tree.getroot()

    root_tag = root.tag
    parsed_result = parse_element_to_dict(root)
    parsed_data = {root_tag : parsed_result} # 将根元素解析至最外层

    with open(output_file, 'w', encoding='utf-8') as outfile:
        yaml.dump(parsed_data, outfile, default_flow_style=False, allow_unicode=True)
        print(f"Successfully parsed to {output_file} output file.")

def parse_element_to_dict(element):
    child = list(element)

    if not child:
        return element.text.strip() if element.text else None # 若没有子元素，则直接返回元素的文本内容

    result = {}

    for c in child:
        child_result = parse_element_to_dict(c)

        if c.tag in result:
            if isinstance(result[c.tag], list): # 比对是否为列表类型
                result[c.tag].append(child_result)
            else:
                result[c.tag] = [result[c.tag], child_result]
        else:
            result[c.tag] = child_result

    return result

if __name__ == '__main__':
    input_file = '../myXML/input_schedule.xml'
    output_file = '../myYAML/output_schedule_ex3.yaml'

    start_time = time.time()
    parse_schedule_xml_to_yaml(input_file, output_file)
    end_time = time.time()
    print(f"{end_time - start_time} seconds")
