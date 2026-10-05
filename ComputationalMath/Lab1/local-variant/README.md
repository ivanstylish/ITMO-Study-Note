# 计算数学 Lab1：简单迭代法源码变体

入口标明变体 15；保留简单迭代求解、对角占优行排列、残差输出，以及 test1–6 输入。Main、FormulaUtils、MatrixPrinter、SimpleIteration 与已有版本不同，原 src 保持原样。

本目录为选择性恢复的源码快照，运行与构建说明见下方资料。原课程已有笔记和实现继续保留。

需要 JDK 与 Gradle Wrapper。算法停止准则为相邻迭代变化小于 eps，不能据此声称已验证全部收敛情况。

只导入白名单文件。依赖、编译输出、服务器安装包、原始私人连接配置与疑似秘密文件均不复制；具体排除项与每个导入文件的 SHA256 见 [导入清单](./import-manifest.json)。

从仓库根目录运行 `node tools/import-local-labs.mjs --verify` 可检查已保存文件完整性。以后重新导入默认 dry-run；脚本拒绝覆盖内容不同的既有文件。
