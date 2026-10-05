# 算法 Lab1：part9–16 独立源码

补充原仓库没有的 part9–16。每个 cpp 都有独立 main，因此必须分别编译。

本目录为选择性恢复的源码快照，运行与构建说明见下方资料。原课程已有笔记和实现继续保留。

部分源码使用 bits/stdc++.h，建议 GCC / Clang 兼容工具链。示例：g++ -std=c++20 part9.cpp -o part9。没有复制将多个 main 链接在一起的原 CMake 文件。

只导入白名单文件。依赖、编译输出、服务器安装包、原始私人连接配置与疑似秘密文件均不复制；具体排除项与每个导入文件的 SHA256 见 [导入清单](./import-manifest.json)。

从仓库根目录运行 `node tools/import-local-labs.mjs --verify` 可检查已保存文件完整性。以后重新导入默认 dry-run；脚本拒绝覆盖内容不同的既有文件。
