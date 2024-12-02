import xlwt

def csv_xls(filename, xlsname):
    file = open(filename, 'r', encoding='=utf-8')
    xls = xlwt.Workbook() # 创建一个excel的工作薄
    sheet = xls.add_sheet('sheet', cell_overwrite_ok=True) # 在工作薄中添加一个工作表

    x = 0 # 表示记录此时写入的行号，从0开始
    for line in file: # 遍历csv文件的每一行
        for column in range(len(line.split(','))): # 以每个逗号来分列
            print(column)
            item = line.split(',')[column]
            sheet.write(x, column, item)
        x += 1
    file.close()
    xls.save(xlsname)

if __name__ == '__main__':
    filename = '../myYAML/output_schedule_ex5.csv'
    xlsname = '../myYAML/result.xls'
    csv_xls(filename, xlsname)