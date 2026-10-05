# Work8：反射、Attribute 与动态 IL

真实 .NET 8 控制台项目：扫描程序集中的自定义 Attribute、按触发器和优先级注册技能、通过 MethodInfo.Invoke 执行；Performance/EmitDemo.cs 另含 DynamicMethod / IL 生成示例，但当前 Main 没有调用它。

本目录为选择性恢复的源码快照，**未在本次整理中构建、运行或验收**。原课程已有笔记和实现继续保留。

需要 .NET 8 SDK。可在此目录运行 dotnet run --project class8.csproj；本次没有运行或进行性能测试。

只导入白名单文件。依赖、编译输出、服务器安装包、原始私人连接配置与疑似秘密文件均不复制；具体排除项与每个导入文件的 SHA256 见 [导入清单](./import-manifest.json)。

从仓库根目录运行 `node tools/import-local-labs.mjs --verify` 可检查已保存文件完整性。以后重新导入默认 dry-run；脚本拒绝覆盖内容不同的既有文件。
