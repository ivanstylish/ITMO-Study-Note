import xml.etree.ElementTree as ET
import csv
import time
def parse_schedule_xml_to_csv(input_file, output_file):
    tree = ET.parse(input_file)
    root = tree.getroot()

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Date', 'DayOfWeek', 'Class', 'TimeOfClass', 'Type', 'Subject', 'Teacher', 'Classroom']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for day in root.findall('day'):
            date = day.get('date')
            for class_data in day.findall('P3110'):
                class_info = {
                    'Date': date,
                    'DayOfWeek': class_data.find('DayOfWeek').text,
                    'Class': class_data.find('Class').text,
                    'TimeOfClass': class_data.find('TimeOfClass').text,
                    'Type': class_data.find('Type').text,
                    'Subject': class_data.find('Subject').text,
                    'Teacher': class_data.find('Teacher').text,
                    'Classroom': class_data.find('Classroom').text
                }
                writer.writerow(class_info)

        print(f"Successfully parsed to '{output_file}'")

if __name__ == '__main__':
    input_file = '../myXML/input_schedule.xml'
    output_file = '../myYAML/output_schedule_ex5.csv'

    start_time = time.time()
    parse_schedule_xml_to_csv(input_file, output_file)
    end_time = time.time()
    print(f"{end_time - start_time} seconds")

