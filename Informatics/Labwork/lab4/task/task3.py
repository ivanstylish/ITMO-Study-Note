import re
import yaml


def parse_xml_to_yaml(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            xml_data = infile.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    day_pattern = r'<day date="([^"]+)">.*?<P3110>(.*?)</P3110>.*?</day>'
    class_pattern = r'<(\w+)>(.*?)</\1>'

    schedule = []
    for day_match in re.finditer(day_pattern, xml_data, re.DOTALL):
        date = day_match.group(1)
        class_data = day_match.group(2)

        class_info = {}
        for class_match in re.finditer(class_pattern, class_data, re.DOTALL):
            tag = class_match.group(1)
            value = class_match.group(2)
            class_info[tag] = value

        day_schedule = {
            'date': date,
            'P3110': [class_info]
        }
        schedule.append(day_schedule)

    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            yaml.dump({'schedule': schedule}, outfile, allow_unicode=True, default_flow_style=False)
            print(f"Output written to {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")


if __name__ == '__main__':
    input_file = '../myXML/input_schedule.xml'
    output_file = '../myYAML/output_schedule_ex2.yaml'
    parse_xml_to_yaml(input_file, output_file)
