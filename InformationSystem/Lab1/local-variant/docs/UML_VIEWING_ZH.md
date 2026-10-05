# UML 图查看与编辑

图文件位于 F:\InfoSystem\Lab1\docs\diagrams，图内没有标题。

| 内容 | draw.io 可编辑文件 | 直接查看 |
| --- | --- | --- |
| 实体类、枚举、关系和日期转换器 | [domain-classes.drawio](diagrams/domain-classes.drawio) | [PNG](diagrams/domain-classes.png) · [SVG](diagrams/domain-classes.svg) |
| 控制器、业务服务、仓库和认证接口 | [application-classes.drawio](diagrams/application-classes.drawio) | [PNG](diagrams/application-classes.png) · [SVG](diagrams/application-classes.svg) |
| 项目包结构及主要依赖 | [packages.drawio](diagrams/packages.drawio) | [PNG](diagrams/packages.png) · [SVG](diagrams/packages.svg) |

打开 [draw.io 在线编辑器](https://app.diagrams.net/)，选择“设备 / Device”，再通过“文件 → 从设备打开 / File → Open From → Device”选择 .drawio 文件。也可以使用 draw.io 桌面版直接打开文件。

每个类的属性、方法和连线均可编辑。类图保留主要属性和关键方法，省略常规 getter / setter 和部分重复 CRUD 方法；参数列表中的 ... 表示为方便排版省略参数。包图包含配置类和 DTO 的归属。

+ 表示 public，- 表示 private，~ 表示包级可见性。实线箭头表示可导航关联；虚线箭头表示依赖；虚线空心三角表示接口实现。0..*、1、0..1 表示关联的数量。

PNG 可直接打开，SVG 可以在浏览器中放大查看。编辑 .drawio 后，通过“文件 → 导出为 / File → Export As”重新导出 PNG 或 SVG；已提供的图片不会随源文件自动变化。

已完成本地 XML 和图片检查，未执行在线导入验证。
