## [主页](../README.md)/Lecture4
## Лекция №4. Тема: «Протоколы, форматы обмена информацией и языки разметки документов. Основы формальных грамматик.»
## 第 4 次讲座。 主题："协议、信息交换格式和文件标记语言。 形式化语法基础。"

### Подготовка к защите 答辩问题：
1. В чём разница между Markup и Markdown?
Markup 和 Markdown 之间有什么区别？  
Языки разметки `Markup`, такие как `HTML`, широко используются в веб-разработке для создания и форматирования веб-контента.    
`Markup`语言如`HTML`广泛应用于网页开发，用于创建和格式化网页内容。  
Язык `Markdown` чаще всего используется для повседневного написания и оформления документов.    
`Markdown`语言通常用于日常写作和文档格式化。  
2. В чём заключается особенность PROTOBUF по сравнению с другими форматами?
比较其他的形式，`PROTOBUF`有什么特别之处？
`PROTOBUF` - это эффективный, независимый от языка, расширяемый и сериализуемый формат обмена данными.    
`PROTOBUF`是一种高效的、语言无关的、可扩展的、可序列化的数据交换格式。    
3. Чем формат CSV отличается от формата TSV? CSV 格式与 TSV 格式有何不同？
Основное различие между ними заключается в использовании разделителей: в формате CSV в качестве разделителя используется запятая (`,`), а в формате TSV в качестве разделителя используется табуляция (`\t`).  
两者的主要区别在于分隔符的使用。CSV格式使用逗号（，）作为分隔符，而TSV格式使用制表符（\t）作为分隔符。
4. Чем обусловлено постоянное появление новых форматов представления данных? 新数据表示格式不断涌现的原因是什么？  
По мере роста объема данных традиционные таблицы и диаграммы перестают удовлетворять наши потребности, Разрабатываются новые форматы представления данных, такие как интерактивные графики и динамические визуализации.
5. Каким образом в формате XML представляются символы ‘>’ и ‘<’?
6. Что такое сериализация данных? 什么是数据序列化？
Сериализация данных - это процесс преобразования структуры данных или объекта в двоичный формат данных, который можно хранить или передавать.Сериализация может использоваться для хранения данных в файле, передачи их по сети или хранения в базе данных.К распространенным форматам сериализации относятся JSON, XML, CSV и т.д.  
数据序列化是将数据结构或对象转换为可存储或传输的二进制数据格式的过程。序列化可用于将数据存储在文件中、通过网络传输或存储在数据库中。常见的序列化格式包括 JSON、XML、CSV 等。
7. Каким образом в YAML обозначаются комментарии? 如何在 YAML 中添加注释？
Using comments in YAML:  
In YAML, comments are denoted by a `#` symbol at the beginning of the line. To add a comment to a line, simply start the line with `#`. 
8. Пояснить, как в языке разметки `Markdown` создать заголовки разных
уровней, оформить код, вывести полужирный, курсивный и
зачеркнутый текст?
**Headers in Markdown**  - полужирный粗体  
*dgssdg* - курсивный斜体  
~~dsfsdf~~ - зачеркнутый删除体  
10. Как расшифровывается аббревиатура SVG? 如何解读 SVG 缩写？
Scalable Vector Graphics - масштабируемая векторная графика — язык разметки масштабируемой векторной графики, созданный Консорциумом Всемирной паутины (W3C) и входящий в подмножество расширяемого языка разметки XML, предназначен для описания двумерной векторной и смешанной векторно/растровой графики в формате XML.  
可缩放矢量图形 - 一种用于可缩放矢量图形的标记语言，由万维网联盟（W3C）创建，是可扩展标记语言 XML 的一个子集，旨在以 XML 格式描述二维矢量和混合矢量/光栅图形。
11. Привести пример использования в языке HTML тега, который создаёт *гиперссылку* на url.举例说明如何使用 HTML 语言中的一个标记，即创建指向网址的超链接
<a href="https://www.google.com">点击我跳转到 Google 网站</a>  
<a href="https://github.com/ivanstylish/ITMO-Study-Note"> click me to go to my study website </a>

12. Какое число структур может представлять собой в закодированном
виде JSON-текст? 有多少种结构能以编码形式表示 JSON 文本？
Существует два типа структур, составляющих JSON-документ: объект и массив. 对象和数组  
```
{
    "name": "Ivan"
    "Age": "20"
}
```
```
[
    {"name": "study-note",
     "url": "https://github.com/ivanstylish/ITMO-Study-Note"}
]
```
