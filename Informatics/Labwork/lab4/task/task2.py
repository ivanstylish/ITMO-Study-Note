import xml.etree.ElementTree as ET
import yaml
import time

def parse_schedule_xml_to_yaml():
    input_file = "../myXML/input_schedule.xml"
    output_file = "../myYAML/output_schedule_ex1.yaml"

    tree = ET.parse(input_file)
    root = tree.getroot()

    parsed_data = parse_xml_to_dict(root)
    root_tag = root.tag

    final_output = {
        root_tag: parsed_data
    }

    with open(output_file, 'w', encoding='utf-8') as outfile:
        yaml.dump(final_output, outfile, default_flow_style=False, allow_unicode=True)
        print(f"output successfully written to {output_file}")

def parse_xml_to_dict(element):
    if len(element) == 0:
        return element.text

    result = {}
    for value in element:
        value_data = parse_xml_to_dict(value)
        if value.tag in result:
            if isinstance(result[value.tag], list):
                result[value.tag].append(value_data)
            else:
                result[value.tag] = [result[value.tag], value_data]
        else:
            result[value.tag] = value_data

    return result

if __name__ == '__main__':
    start_time = time.time()
    parse_schedule_xml_to_yaml()
    end_time = time.time()
    print(f"total time: {end_time - start_time}")
