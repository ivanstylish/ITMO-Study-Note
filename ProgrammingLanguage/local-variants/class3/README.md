# Class3：角色战斗 .NET 源码变体

保留 BattleManager、Legend、Garen、Mantis 和控制台入口的另一套实现。

本目录为选择性恢复的源码快照，运行与构建说明见下方资料。原课程已有笔记和实现继续保留。

需要 .NET 8 SDK；与 work3 的已有实现并存，尚未构建。

只导入白名单文件。依赖、编译输出、服务器安装包、原始私人连接配置与疑似秘密文件均不复制；具体排除项与每个导入文件的 SHA256 见 [导入清单](./import-manifest.json)。

从仓库根目录运行 `node tools/import-local-labs.mjs --verify` 可检查已保存文件完整性。以后重新导入默认 dry-run；脚本拒绝覆盖内容不同的既有文件。
