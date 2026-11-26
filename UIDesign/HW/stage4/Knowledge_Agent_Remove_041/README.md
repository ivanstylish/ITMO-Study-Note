# 移除 Knowledge Agent 历史记录 #041

1. 解压后，在这个文件夹打开 PowerShell，运行：

   ```powershell
   powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File .\install-into-plugin.ps1
   ```

2. 选择你之前在 Figma 安装的 Knowledge Agent 开发插件的 `manifest.json`。安装器会备份旧插件。
3. 在 Figma 桌面版切换到原文件的 `Knowledge Agent new` 页面。从 **Plugins → Development** 运行 **Knowledge Agent - Remove History 041**，点击 **移除 #041**。

补丁删除两种配色里的最近第二条、#041 历史列表项及对应详情，收起列表空行。处理报告的历史入口打开历史列表，原来借用 #041 详情展示笔记的图谱入口改为打开包含两条笔记的既有处理报告。

#045 和 #046 是独立记录，保留在其流程分支内。
