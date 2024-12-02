import re
import yaml
import time


def parse_xml_to_yaml(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile:
        xml_data = infile.read()

    day_pattern = r'<day date="([^"]+)">.*?<P3110>(.*?)</P3110>.*?</day>'
    class_pattern = r'<(\w+)>(.*?)</\1>'

    schedule = []
    for day_match in re.finditer(day_pattern, xml_data, re.DOTALL): # pattern string flags=0
        date = day_match.group(1) # 先是日期组，而后时当天课程组
        class_data = day_match.group(2)

        class_info = {}
        for class_match in re.finditer(class_pattern, class_data, re.DOTALL):
            tag = class_match.group(1)
            value = class_match.group(2)
            class_info[tag] = value

        day_schedule = {
            'Date': date,
            'P3110': [class_info]
        }
        schedule.append(day_schedule)

    with open(output_file, 'w', encoding='utf-8') as outfile:
            yaml.dump({'schedule': schedule}, outfile, allow_unicode=True, default_flow_style=False)
            print(f"Output written to {output_file}")


if __name__ == '__main__':
    input_file = '../myXML/input_schedule.xml'
    output_file = '../myYAML/output_schedule_ex2.yaml'

    start_time = time.time()
    parse_xml_to_yaml(input_file, output_file)
    end_time = time.time()
    print(f"{end_time - start_time} seconds")
