# 查看与编辑 UML 图

`.puml` 是 PlantUML 的文本源文件，描述类、包、属性、方法和关系；它本身不是图片。修改源文件后，需要交给 PlantUML 渲染成 SVG 或 PNG。

## 直接查看项目已有图片

只想看图时，不需要上传到网站。打开 `F:\InfoSystem\Lab1\docs\uml` 中对应的 `.svg` 或 `.png` 即可，SVG 可以直接用 Chrome 或 Edge 打开并放大。

| 图 | 可修改的源文件 | 已生成的图片 |
|---|---|---|
| 领域实体类图 | `classes.puml` | `classes.svg`、`classes.png` |
| 应用类图，包含控制器、服务与账号相关类 | `application-classes.puml` | `application-classes.svg`、`application-classes.png` |
| 包图 | `packages.puml` | `packages.svg`、`packages.png` |

## 可以使用的在线网站

| 网站 | 用法 |
|---|---|
| [PlantUML 官方在线服务器](https://www.plantuml.com/plantuml/uml/) | 粘贴 PlantUML 文本，点击 Submit 或等待自动刷新，查看 PNG / SVG |
| [PlantUML 官方 Web Editor](https://editor.plantuml.com/) | 在编辑区修改源代码并查看图形预览 |
| [PlantText](https://www.planttext.com/) | 粘贴源代码，在编辑器旁预览；需要时刷新图形并保存结果 |

PlantUML 官方服务器支持 PNG 和 SVG 输出，说明见 [PlantUML Server 文档](https://plantuml.com/es/server)。PlantText 的自动保存与预览刷新功能见其 [官方说明](https://blog.planttext.com/2024/02/01/planttext-release-version-21/)。

具体操作：

1. 在 IDEA 或记事本中打开一个 `.puml` 文件，例如 `packages.puml`。
2. 复制文件的完整内容，包括开头的 `@startuml` 和结尾的 `@enduml`；不要复制 Markdown 的三个反引号。
3. 打开上述网站，替换编辑区中的示例代码。
4. 点击 Submit / Refresh，或者等待自动预览。
5. 查看图形后选择 SVG 或 PNG；在图形页面保存图片。答辩展示需要放大时，优先保存 SVG。

每次粘贴一份图的完整内容即可。若只改了 `.puml`，同目录旧的 `.svg` / `.png` 不会自动变化，需要重新生成。
