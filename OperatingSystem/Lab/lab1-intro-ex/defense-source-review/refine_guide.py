from pathlib import Path

folder = Path(__file__).resolve().parent
path = folder / "guide-draft.md"
text = path.read_text(encoding="utf-8")
text = text.replace("最后进行问答和现场演示。", "最后进行闭卷复述和问答。")
start = text.index("## E. 现场展示与代码理解")
end = text.index("### E4. 实际脚本每一层负责什么？", start)
text = (text[:start]
        + "## E. 代码与脚本原理 / Принципы работы кода и сценариев\n\n"
        + text[end:].replace("### E4. 实际脚本每一层负责什么？", "### E1. 实际脚本每一层负责什么？", 1))
start = text.index("**中文：**若老师要求重新做完整统计，应在新的工作副本")
end = text.index("---\n\n## F.", start)
text = text[:start] + text[end:]
start = text.index("### 第三轮：现场演示")
end = text.index("### 容易答错的句子", start)
text = (text[:start]
        + "### 第三轮：闭卷复述与问答 / Третий проход: пересказ и вопросы\n\n"
        + "- [ ] 不看资料，用俄语讲清各节的目的、结果和限制。/ Без подсказок объяснить цель, результат и ограничения каждого раздела.\n"
        + "- [ ] 手算 A 的 SE 与 CI；解释 pilot 怎样选择 N。/ Рассчитать SE и ДИ для A и объяснить выбор N.\n"
        + "- [ ] 指着三幅图说出坐标、数据单位和结论。/ Объяснить оси, единицы и выводы трёх рисунков.\n"
        + "- [ ] 回答 D 部分的问题；不懂的知识点再回到对应教材页。/ Ответить на вопросы раздела D и повторить непонятные темы по указанным страницам.\n\n"
        + text[end:])
text = text.replace("用于核对任务范围、baseline 与答辩演示。", "用于核对任务范围、baseline 和知识要求。")
assert "defense-demo" not in text
assert "现场演示" not in text
assert "head -n" not in text
path.write_text(text, encoding="utf-8")
print("Removed live demonstration instructions; retained report explanations and script principles.")
