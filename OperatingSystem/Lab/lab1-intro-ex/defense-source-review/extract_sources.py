from pathlib import Path
import json
from pypdf import PdfReader

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
sources = [root / "Lecture/BPF-Performance-Tools.pdf", root / "Lab/lab1-intro-ex/report-completion-20261012/ОС-P3310 Чжун Цзяцзюнь intro_exp.pdf"]
for source in sources:
    reader = PdfReader(source)
    pages = [{"pdf_page": i + 1, "text": page.extract_text() or ""} for i, page in enumerate(reader.pages)]
    prefix = "bpf" if source.name.startswith("BPF") else "report"
    (out / (prefix + "-pages.json")).write_text(json.dumps(pages, ensure_ascii=False), encoding="utf-8")
    (out / (prefix + "-text.txt")).write_text("\n\n".join("--- PDF PAGE " + str(p["pdf_page"]) + " ---\n" + p["text"] for p in pages), encoding="utf-8")
    print(prefix, len(pages), "pages extracted", flush=True)
