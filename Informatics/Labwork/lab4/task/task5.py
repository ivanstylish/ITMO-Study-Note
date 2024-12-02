import xml.etree.ElementTree as ET
import csv
import time
def parse_schedule_xml_to_csv(input_file, output_file):
    def collect_fields_and_data(element, current_path, fields, data_row):
        # 如果元素有属性，将它们添加为字段
        for attr_name, attr_value in element.attrib.items():
            field_name = f"{current_path}/{attr_name}" if current_path else attr_name
            if field_name not in fields:
                fields.add(field_name)
            data_row[field_name] = attr_value

        # 遍历子元素
        for child in element:
            field_name = f"{current_path}/{child.tag}" if current_path else child.tag
            if field_name not in fields:
                fields.add(field_name)

            if child.text and child.text.strip():
                data_row[field_name] = child.text.strip()

            collect_fields_and_data(child, field_name, fields, data_row)

    tree = ET.parse(input_file)
    root = tree.getroot()

    fields = set()  # 用于存储所有唯一字段
    data_rows = []  # 用于存储每一行数据

    for element in root:
        data_row = {}
        collect_fields_and_data(element, '', fields, data_row)
        data_rows.append(data_row)

    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = sorted(fields)  # 按字母顺序排列标题
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data_rows)

    print(f"Successfully parsed to '{output_file}'")

if __name__ == '__main__':
    input_file = '../myXML/input_schedule.xml'
    output_file = '../myCSV/output_schedule_ex5.csv'

    start_time = time.time()
    parse_schedule_xml_to_csv(input_file, output_file)
    end_time = time.time()
    print(f"{end_time - start_time} seconds")


