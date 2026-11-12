# UCI 856 原始数据

`students.csv` 为 UCI 官方压缩包中 `DATA (1).csv` 的原始内容，仅重命名文件，未修改数据。

- 来源：[Higher Education Students Performance Evaluation](https://archive.ics.uci.edu/dataset/856)
- 官方下载：[原始数据压缩包](https://archive.ics.uci.edu/static/public/856/higher%2Beducation%2Bstudents%2Bperformance%2Bevaluation.zip)
- 作者：Yilmaz, N. 与 Şekeroğlu, B. (2019)
- DOI：[10.24432/C51G82](https://doi.org/10.24432/C51G82)
- 许可：CC BY 4.0；保留以上署名和来源。
- 获取日期：2026-11-10。
- SHA256：`d5905d231bedd7e4cdcf708fab55fc65b79dfe12012e846eccad3e88b5ecb019`

145 行，33 列：学生 ID、31 个候选特征、GRADE。正类为 `GRADE >= 3`。
`STUDENT ID` 与 `GRADE` 均不进入模型；`COURSE ID` 为课程类别，按任务保留。
原始特征列 1–30 的可读名称见 `experiment.py` 中的 `FEATURES`，按原顺序一一对应，最后一项对应 COURSE ID。
