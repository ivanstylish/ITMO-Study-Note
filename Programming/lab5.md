### Вопросы к защите лабораторной работы:
1. Коллекции. Сортировка элементов коллекции. Интерфейсы java.util.Comparable и java.util.Comparator. 集合 对集合中的元素进行排序 接口 java.util.Comparable 和 java.util.Comparator.
Метод sort() класса Collections используется для сортировки списка в Java. Основное различие между ними заключается в том, что Comparable - это внутренний компаратор, а Comparator - внешний.

2. Категории коллекций - списки, множества. Интерфейс java.util.Map и его реализации. 集合的类别有列表、集合。 接口 java.util.Map 及其实现。
Интерфейс Map. Он предоставляет возможность доступа к коллекции пар ключ-значение. Классами реализации интерфейса Map являются HashMap, Hashtable, TreeMap, LinkedHashMap и так далее.  
В Java основные типы коллекций можно разделить на четыре категории: `List, Set, Queue и Map`.  
地图接口。 它提供了访问键值对集合的能力。 实现 Map 接口的类有 HashMap、Hashtable、TreeMap、LinkedHashMap 等。
在 Java 中，主要的集合类型可分为四类："列表（List）"、"集合（Set）"、"队列（Queue）"和 "地图（Map）"。  

3. Параметризованные типы. Создание параметризуемых классов. Wildcard-параметры. 泛型类型 泛型类的创建 通配符参数(泛型)
Разрешить использование параметров типа в классах, интерфейсах или методах для улучшения переиспользуемости кода и безопасности типов  
```
public class Box<T> {
    private T content;
    public void set(T content) { this.content = content; }
    public T get() { return content; }
}
```  

`? extends T`: 接受 T 或其子类（上界通配符）。  
`? extends T`: Принимает T или его подклассы (подстановочный знак верхней границы).  
`? super T`: 接受 T 或其父类（下界通配符）  
`? super T`: принимает T или его родителя (подстановочный знак нижней границы)  

4. Классы-оболочки. Назначение, область применения, преимущества и недостатки. Автоупаковка и автораспаковка. 包装类。 目的、应用范围、优缺点。 自动包装和自动拆装。
например, `Integer`, `Double`, Используется для преобразования базовых типов в объекты, Разрешите базовым типам участвовать в объектно-ориентированных операциях (например, хранение коллекций).
优点：Совместим с дженериками, поддерживает нулевые значения.
缺点：Накладные расходы памяти и немного меньшая производительность.  
```
Integer a = 10;      // 自动装箱：int → Integer
int b = a;           // 自动拆箱：Integer → int
```  

5. Потоки ввода-вывода в Java. Байтовые и символьные потоки. "Цепочки" потоков (Stream Chains). Java 中的 I/O 流。 字节流和字符流 "流链（Stream Chains）"。
Печать на экране(`System.out.println()`)
пользовательский ввод(`System.in`)
Байтовые потоки (字节流): `InputStream, OutputStream`, Символьные потоки (字符流): `Reader, Writer`（处理文本数据，如.txt）。  


6. Работа с файлами в Java. Класс java.io.File. 用 Java 处理文件 类 java.io.File.File.Class
Класс java.io.File: 表示文件或目录路径，提供操作方法：Указывает путь к файлу или каталогу и предоставляет метод операции:  

7. Пакет java.nio - назначение, основные классы и интерфейсы. java.nio 软件包 - 目的、主要类和接口。
- Назначение: Обеспечивает эффективные неблокирующие операции ввода-вывода с поддержкой буферов и каналов.
- Основные классы: `ByteBuffer, MappedByteBuffer, Channel, Selector`
   - Path: 表示文件路径。 Указывает путь к файлу.
   - Files: 提供文件操作方法（如复制、删除）Предоставьте методы работы с файлами (например, копирование, удаление).
   - Channels: 如 `FileChannel`，用于高效数据传输。 Например, `FileChannel` для эффективной передачи данных.
- Интерфейсы: `ReadableByteChannel, InterruptibleChannel`

8.  Утилита javadoc. Особенности автоматического документирования кода в Java. javadoc 工具。 Java 自动代码文档的特点。
使用 `/** ... */` 注释。  
Используйте `/** ... */` аннотацию.
支持标签如 `@param描述参数, @return描述返回值, @throws描述可能抛出的异常。  `。  
Поддерживайте такие теги, как`@param, @return, @throws`.


实验代码框架：
主要分为五个包加main实现主类：其中有关于命令，异常类，管理包，实体模型包，工具包（将文件输出保存为json格式）。  
在manager包中有这两个类，这个类中一开始定义了三个变量其中的关于命令的集合collecion，按要求是用Stack集合来实现的。IdGenerator类是实现自动生成并递增产品id。  
这段代码定义了一个名为 FileUtils 的工具类，位于 util 包中。该类主要用于文件的读写操作。  