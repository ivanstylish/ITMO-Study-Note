import time


def parse_schedule_xml_to_yaml(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile:
            xml_data = infile.read()

    schedule = {}
    days = xml_data.split("<day date=")
    for day in days[1:]: # [1:]为了确保解析时跳过无关的内容
        date = day.split('"')[1] # 提取日期值
        if date not in schedule:
            schedule[date] = {'date': date, 'classes': []}
        classes = day.split("<P3110>")[1:]
        for class_data in classes:
            dayOfWeek = find_xml_value(class_data, "DayOfWeek")
            class_num = find_xml_value(class_data, "Class")
            time = find_xml_value(class_data, "TimeOfClass")
            type = find_xml_value(class_data, "Type")
            subject = find_xml_value(class_data, "Subject")
            teacher = find_xml_value(class_data, "Teacher")
            classroom = find_xml_value(class_data, "Classroom")
            schedule[date]['classes'].append({
                'dayOfWeek': dayOfWeek,
                'class_num': class_num,
                'time': time,
                'type': type,
                'subject': subject,
                'teacher': teacher,
                'classroom': classroom
            })


    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write("schedule:\n")
        for day in schedule.values():
            outfile.write(f"- date: \"{day['date']}\"\n")
            outfile.write(f"  P3110: \n")
            for cls in day['classes']:
                outfile.write(f"  - DayOfWeek: {cls['dayOfWeek']}\n")
                outfile.write(f"    Class: {cls['class_num']}\n")
                outfile.write(f"    TimeOfClass: {cls['time']}\n")
                outfile.write(f"    Type: {cls['type']}\n")
                outfile.write(f"    Subject: {cls['subject']}\n")
                outfile.write(f"    Teacher: {cls['teacher']}\n")
                outfile.write(f"    Classroom: {cls['classroom']}\n")
        print(f"Output written to {output_file}")

def find_xml_value(data, tag):
    tag_start = f"<{tag}>"
    tag_end = f"</{tag}>"
    start_value = data.find(tag_start) + len(tag_start)
    end_index = data.find(tag_end)
    return data[start_value:end_index].strip()

if __name__ == "__main__":
    input_file = "../myXML/input_schedule.xml"
    output_file = "../myYAML/output_schedule.yaml"

    start_time = time.time()
    parse_schedule_xml_to_yaml(input_file, output_file)
    end_time = time.time()
    print(f"{end_time - start_time} seconds")