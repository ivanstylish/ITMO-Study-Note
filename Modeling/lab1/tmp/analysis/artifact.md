# Template contract for laboratory report 1 variant 115

## Reference

- Retained source: `D:\Study-Note\Modeling\lab1\3315_Барсуков_Горляков_УИР1.docx`
- SHA-256: `13511c46a5691eda41ba20942897da409b48666286b54fe0960fcf51180769a3`
- Render: 13 A4 pages from Microsoft Word 2021 in `template_render_word`
- Sections: one portrait section
- Evidence: `template-style-evidence.json`, section, heading, image, field, and comment audits

## Page system

- A4 portrait, 8.26 by 11.69 inches
- Margins: 0.50 inches on every side
- Header and footer distance: approximately 0.49 inches
- Different first page enabled
- Centered Arabic page numbers in default and even-page footers
- One section; page breaks separate the cover, assignment, and work stages

## Typography and paragraph rhythm

- Primary typeface: Times New Roman
- Cover institution lines: 14 pt, centered, 1.5 line spacing
- Cover report title: 14 to 16 pt, bold, centered
- Cover author and reviewer block: 14 pt, right aligned
- Body: 14 pt Times New Roman, justified or left aligned, 1.0 to 1.15 line spacing
- Major headings: 16 pt bold, black
- Stage headings: 14 pt bold, black; selected lead words may be underlined to match the source pattern
- Captions and notes: 10 to 12 pt
- Equations: centered; use native Word math or rendered formula images

## Tables and figures

- Tables use black outer and internal borders, centered numeric cells, and bold header rows
- Form 1 and Form 2 use two descriptor columns plus six sample-size columns
- Form 3 uses one label column plus ten lag columns
- The source uses full-width plots centered within the text area
- Figures have Russian titles and axis labels; conclusions follow immediately after the relevant table or figure

## Content flow and slots

1. Cover: preserve the latest saved identity fields exactly: Чжун Цзяцзюнь, group P3310, teacher Тропченко Андрей Александрович, variant 115, and year 2026. Correct the cover break so the city/year remains on page 1.
2. Assignment and objective: preserve the supplied laboratory objective and required report contents, but normalize the list layout.
3. Work progress: replace every result, table, figure, equation, algorithm, and conclusion from variant 16 with calculations for variant 115.
4. Conclusions: replace completely with evidence from variant 115.
5. Add Chinese translations after key Russian explanations and conclusions, using smaller italic text without changing the primary Russian-report structure.

## Stable locators

- Cover slots are the body paragraphs containing `Вариант:`, `Отчёт принят`, and `г. Санкт-Петербург`.
- The body rewrite begins after the cover content and uses the source section properties, footer relationships, and style definitions.
- Preserve the first-page/header and default/even-footer parts. Replace the main document body content and body image relationships intentionally.

## Package preservation and intentional changes

- Preserve: page size, margins, section behavior, styles, theme, numbering definitions, first-page header, footer page-number fields, core document properties, and cover identity text.
- Replace intentionally: all old body tables, images, variant-16 calculations, old conclusions, and old equations.
- Remove intentionally: 13 unresolved reviewer comments and their anchors, because they belong to the old variant-16 report.
- New media: six charts and rendered equation images for variant 115.

## Fidelity gates

- Reference SHA-256 must remain unchanged.
- Final document must stay recognizably source-derived in cover, margins, typeface, heading hierarchy, table forms, footer numbering, and stage order.
- Every page must render without clipping, overlap, broken glyphs, table overflow, or orphaned headings.
- All numerical values must trace to the 300 values in variant 115 and the stated formulas.
