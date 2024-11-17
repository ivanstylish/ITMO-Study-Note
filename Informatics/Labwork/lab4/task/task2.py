import xml.etree.ElementTree as ET
import yaml
import time

def parse_schedule_xml_to_yaml(input_file, output_file):
    tree = ET.parse(input_file)
    root = tree.getroot()

    schedule = []

    for day in root.findall('day'):
        date = day.get('date')

        day_schedule = {
            'date': date,
            'P3110': []
        }

        # 解析课程信息
        classes = day.findall('P3110')
        for class_data in classes:
            class_info = {}
            for tag in ['DayOfWeek', 'Class', 'TimeOfClass', 'Type', 'Subject', 'Teacher', 'Classroom']:
                element = class_data.find(tag)
                class_info[tag] = element.text

            day_schedule['P3110'].append(class_info)

        schedule.append(day_schedule)

    with open(output_file, 'w', encoding='utf-8') as outfile:
            yaml.dump({'schedule': schedule}, outfile, allow_unicode=True, default_flow_style=False)
            print(f"Output successfully written to '{output_file}'")

if __name__ == '__main__':
    input_file = "../myXML/input_schedule.xml"
    output_file = "../myYAML/output_schedule_ex1.yaml"

    start_time = time.time()
    parse_schedule_xml_to_yaml(input_file, output_file)
    end_time = time.time()
    print(f"{end_time - start_time} seconds")
