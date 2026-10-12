# Intro-Exp：PDF 对应源码、仅改措辞修订稿与独立审核

## 文件用途

- `faithful/report.typ`：复制自学科文件夹的原始 report.typ，源文件字节完全相同。`faithful/report.pdf` 为编译验证稿；11 页文字与渲染像素均与原《Intro-Exp-实验报告-复核版.pdf》一致。新编译文件的创建时间等 PDF 元数据可以不同。
- `revised/report.typ`、`revised/report.pdf`：仅修改措辞与材料链接，原数值、表格、图表及日期保留，未写入 10 月 12 日的新 C。
- `analysis/new-data-comparison-zh.md`：新旧诊断差异和 C 等待时间说明。
- `analysis/report-requirements-review-zh.md`：只针对原 11 页报告的逐项要求审核，并区分本次修订。
- `analysis/prose-changes.diff`：所有措辞修改的可复核差异。
- `analysis/background-comparison.csv`、`tool-comparison.csv`、`comparison-statistics.json`：独立统计与来源。
- `data/diag-20261012-173446/`：本次原始诊断目录的复制与原文件时间标签。
- `data/report-reference/`：用于此次比较的旧 CSV 复制。

原报告、原 report.typ 与所有原结果均保留；GitHub 只作为本地报告中的链接，没有上传或修改任何仓库内容。

## 编译方法

每个版本必须保留同级 `report-assets/final/` 中的两幅 SVG。只上传一个 .typ 而不上传图片，会产生图片找不到错误。

使用 Typst 0.15.1 的内置字体，可以复现本次验证版面：

```bash
typst compile --ignore-system-fonts faithful/report.typ faithful/report.pdf
typst compile --ignore-system-fonts revised/report.typ revised/report.pdf
```

在 Typst 在线编辑器中分别上传相应版本的 report.typ 与 report-assets 目录。若在线编译器版本不同，分页或细节可能改变。本次复现检查使用与原 PDF 相同的 Typst 0.15.1。

本次没有重新运行课程遍历或 stress-ng，仅处理保存的数据、复制材料、编译和检查 PDF。
