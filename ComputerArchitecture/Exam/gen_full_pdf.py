#!/usr/bin/env python3
"""Generate comprehensive bilingual Computer Architecture Exam Q&A PDF (2026)."""
from fpdf import FPDF
import os

class ExamPDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.set_auto_page_break(True, 15)
        fd = r'C:\Windows\Fonts'
        self.add_font('Ar', '', os.path.join(fd, 'arial.ttf'), uni=True)
        self.add_font('Ar', 'B', os.path.join(fd, 'arialbd.ttf'), uni=True)
        self.add_font('Ar', 'I', os.path.join(fd, 'ariali.ttf'), uni=True)
        self.add_font('NS', '', os.path.join(fd, 'NotoSansSC-VF.ttf'), uni=True)
        self.qnum = 0

    def header(self):
        if self.page_no() <= 1: return
        self.set_font('Ar', 'I', 7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 4, 'Computer Architecture Exam QA | ITMO 2026', align='C')
        self.ln(6)

    def footer(self):
        self.set_y(-12)
        self.set_font('Ar', 'I', 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, f'Page {self.page_no()}/{{nb}}', align='C')

    def add_qa(self, cn_q, ru_q, cn_a, ru_a):
        self.qnum += 1
        if self.get_y() > 225: self.add_page()
        self.set_font('Ar', 'B', 10)
        self.set_fill_color(240, 245, 250)
        self.cell(0, 7, f'Q{self.qnum}', fill=True, ln=True)
        self.set_font('NS', '', 9)
        self.set_text_color(180, 30, 30)
        self.multi_cell(0, 5, cn_q)
        self.ln(1)
        self.set_font('Ar', '', 9)
        self.set_text_color(30, 30, 180)
        self.multi_cell(0, 5, ru_q)
        self.ln(1)
        self.set_text_color(0, 0, 0)
        self.set_font('NS', '', 8.5)
        self.set_fill_color(255, 250, 245)
        self.cell(0, 5, '  CN (~30s)', fill=True, ln=True)
        self.set_font('NS', '', 8.5)
        self.multi_cell(0, 4.5, cn_a)
        self.ln(2)
        self.set_font('Ar', '', 8.5)
        self.set_fill_color(245, 248, 255)
        self.cell(0, 5, '  RU (~30s)', fill=True, ln=True)
        self.set_font('Ar', '', 8.5)
        self.multi_cell(0, 4.5, ru_a)
        self.ln(3)
        self.set_draw_color(200, 200, 200)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

pdf = ExamPDF()
pdf.alias_nb_pages()
pdf.add_page()
pdf.ln(30)
pdf.set_font('Ar', 'B', 24)
pdf.set_text_color(20, 60, 120)
pdf.cell(0, 12, 'Computer Architecture', align='C', ln=True)
pdf.set_font('Ar', 'B', 18)
pdf.cell(0, 10, 'Exam Q&A Reference Guide 2026', align='C', ln=True)
pdf.ln(5)
pdf.set_font('NS', '', 14)
pdf.set_text_color(60, 60, 60)
pdf.cell(0, 10, 'ITMO University', align='C', ln=True)
pdf.ln(5)
pdf.set_font('Ar', '', 10)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 8, '234 Questions | Bilingual | Each answer ~30s oral', align='C', ln=True)
pdf.cell(0, 8, 'Generated: 2026-06-05', align='C', ln=True)
pdf.ln(10)

# ====== Q&A DATA ======
