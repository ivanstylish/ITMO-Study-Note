import xml.etree.ElementTree as ET
import yaml
import time

def parse_schedule_xml_to_yaml(input_file, output_file):
    tree = ET.parse(input_file)
    root = tree.getroot()

    schedule = []

    if root.tag.strip() != 'Schedule':
        print(f"Error: Root element is not 'Schedule'. Found '{root.tag}' instead.")
        return

    for day in root.findall('day'):
        date = day.get('date')
        if not date:
            print(f"Error: Could not find the element 'day'")
            return

        day_schedule = {
            'date': date,
            'P3110': []
        }

        classes_list = day.findall('P3110')
        if not classes_list:
            print(f"Error: Could not find element 'P3110'")
            return

        for class_data in classes_list:
            class_info = {}
            for tag in ['DayOfWeek', 'Class', 'TimeOfClass', 'Type', 'Subject', 'Teacher', 'Classroom']:
                element = class_data.find(tag)
                class_info[tag] = element.text

            if class_info:
                day_schedule['P3110'].append(class_info)

        if day_schedule['P3110']:
            schedule.append(day_schedule)

    with open(output_file, 'w', encoding='utf-8') as outfile:
            yaml.dump({'schedule': schedule}, outfile, default_flow_style=False, allow_unicode=True)
            print(f"Successfully parsed to {output_file} output file.")

if __name__ == '__main__':
    input_file = '../myXML/input_schedule.xml'
    output_file = '../myYAML/output_schedule_ex3.yaml'
    parse_schedule_xml_to_yaml(input_file, output_file)

    start_time = time.time()
    parse_schedule_xml_to_yaml(input_file, output_file)
    end_time = time.time()
    print(f"{end_time - start_time} seconds")