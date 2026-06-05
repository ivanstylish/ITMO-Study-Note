#!/usr/bin/env python3
from fpdf import FPDF
import os, json

class ExamPDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.set_auto_page_break(True, 15)
        font_dir = r'C:\Windows\Fonts'
        self.add_font('Arial', '', os.path.join(font_dir, 'arial.ttf'), uni=True)
        self.add_font('Arial', 'B', os.path.join(font_dir, 'arialbd.ttf'), uni=True)
        self.add_font('Arial', 'I', os.path.join(font_dir, 'ariali.ttf'), uni=True)
        self.add_font('NotoSans', '', os.path.join(font_dir, 'NotoSansSC-VF.ttf'), uni=True)
        self.q_num = 0

    def header(self):
        if self.page_no() <= 1: return
        self.set_font('Arial', 'I', 7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 4, 'Computer Architecture Exam Q&A \u00b7 \u0410\u0440\u0445\u0438\u0442\u0435\u043a\u0442\u0443\u0440\u0430 \u043a\u043e\u043c\u043f\u044c\u044e\u0442\u0435\u0440\u043e\u0432 \u00b7 \u8ba1\u7b97\u673a\u4f53\u7cfb\u7ed3\u6784', align='C')
        self.ln(6)

    def footer(self):
        self.set_y(-12)
        self.set_font('Arial', 'I', 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, f'Page {self.page_no()}/{{nb}}', align='C')

    def add_qa(self, q):
        self.q_num += 1
        if self.get_y() > 230: self.add_page()
        cn_q, ru_q, cn_a, ru_a = q['cn_q'], q['ru_q'], q['cn_a'], q['ru_a']
        # Question header
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(240, 245, 250)
        self.cell(0, 7, f'Q{self.q_num}', fill=True, ln=True)
        self.set_font('NotoSans', '', 9)
        self.set_text_color(180, 30, 30)
        self.multi_cell(0, 5, cn_q)
        self.ln(1)
        self.set_font('Arial', '', 9)
        self.set_text_color(30, 30, 180)
        self.multi_cell(0, 5, ru_q)
        self.ln(1)
        # Chinese answer
        self.set_text_color(0, 0, 0)
        self.set_font('NotoSans', '', 8.5)
        self.set_fill_color(255, 250, 245)
        self.cell(0, 5, '  \u4e2d\u6587  (Chinese, ~30s)', fill=True, ln=True)
        self.set_font('NotoSans', '', 8.5)
        self.multi_cell(0, 4.5, cn_a)
        self.ln(2)
        # Russian answer
        self.set_font('Arial', '', 8.5)
        self.set_fill_color(245, 248, 255)
        self.cell(0, 5, '  \u0420\u0443\u0441\u0441\u043a\u0438\u0439  (Russian, ~30s)', fill=True, ln=True)
        self.set_font('Arial', '', 8.5)
        self.multi_cell(0, 4.5, ru_a)
        self.ln(3)
        # Separator
        self.set_draw_color(200, 200, 200)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

pdf = ExamPDF()
pdf.alias_nb_pages()
# Title page
pdf.add_page()
pdf.ln(30)
pdf.set_font('Arial', 'B', 24)
pdf.set_text_color(20, 60, 120)
pdf.cell(0, 12, 'Computer Architecture', align='C', ln=True)
pdf.set_font('Arial', 'B', 18)
pdf.cell(0, 10, 'Exam Q&A Reference Guide 2026', align='C', ln=True)
pdf.ln(5)
pdf.set_font('NotoSans', '', 14)
pdf.set_text_color(60, 60, 60)
pdf.cell(0, 10, '\u8ba1\u7b97\u673a\u4f53\u7cfb\u7ed3\u6784 | \u0410\u0440\u0445\u0438\u0442\u0435\u043a\u0442\u0443\u0440\u0430 \u043a\u043e\u043c\u043f\u044c\u044e\u0442\u0435\u0440\u043e\u0432', align='C', ln=True)
pdf.ln(5)
pdf.set_font('Arial', '', 11)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 8, '237 Q&A \u00b7 \u0414\u0432\u0443\u044f\u0437\u044b\u0447\u043d\u044b\u0439 \u0441\u043f\u0440\u0430\u0432\u043e\u0447\u043d\u0438\u043a \u00b7 \u53cc\u8bed\u53c2\u8003', align='C', ln=True)
pdf.cell(0, 8, 'Each answer \u2248 30 seconds oral response', align='C', ln=True)
pdf.ln(5)
pdf.set_font('Arial', '', 9)
pdf.cell(0, 6, 'Generated: 2026-06-05 | ITMO University', align='C', ln=True)

# Load Q&A data from JSON
with open(r'D:\Study-Note\ComputerArchitecture\Exam\qa_data.json', 'r', encoding='utf-8') as f:
    qa_list = json.load(f)

for q in qa_list:
    pdf.add_qa(q)

output = r'D:\Study-Note\ComputerArchitecture\Exam\Computer_Architecture_QA_2026.pdf'
pdf.output(output)
print(f'Done! {pdf.q_num} questions, {pdf.page_no()} pages')
print(f'Saved to: {output}')
