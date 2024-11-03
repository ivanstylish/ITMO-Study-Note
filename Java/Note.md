## [主页](../README.md)/[Java](readme.md)/代码笔记

### Java主类结构
- Java程序的基本组成单元是类，类体中又包括属性与方法两部分
  - 通常将类的属性称为类的**全局变量**（成员变量），将方法中的属性称为**局部变量**。全局变量声明在类体中，局部变量声明在方法体中。全局变量和局部变量都有各自的应用范围 
- 每一个应用程序都必须包含一个main()方法，含有main()方法的类称为主类
- 项目project、包package和类java class
- main()方法是类体中的主方法。该方法从“{”开始，至“}”结束。
**public、static和void**分别是main()方法的**权限修饰符、静态修饰符和返回值修饰符**，Java程序中的main()方法必须声明为`public static void。String[] args`是一个字符串类型的数组，它是`main()`方法的参数，main()方法是程序开始执行的位置。
**static**修饰符表示该方法是一个静态方法，可以不通过创建类的实例对象来调用。一个类中可以有无数个实例，但只有一个静态域。

- 实例代码

```
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello world!");
    }
}
```

### 基本数据类型
Java中有8种基本数据类型来存储数值、字符和布尔值
![](/Java/pic/java1.png)

- #### 整数类型
  - 整数类型用来存储整数数值，即没有小数部分的数值。可以是正数，也可以是负数。整型数据在Java程序中有3种表示形式，分别为**十进制**、**八进制**和**十六进制**。
  - 整型数据根据它所占内存大小的不同，可分为`byte、short、int和long` 4种类型。
  - 在定义以上4种类型变量时，要注意变量的取值范围，超出相应范围就会出错。
对于long型值，若赋给的值大于int型的最大值或小于int型的最小值，则需要在数
字后加L或l，表示该数值为长整数，如long num = 2147483650L。
  
|数据类型|内存空间(8位等于1字节)|取值范围|
|:----:|:----|:----|
|byte|8位|-128~127|
|short|16位|-32768~32767|
|int|32位|-2147483648~2147483647|
|long|64位|-9223372036854775808~9223372036854775807|

定义int型变量
```
int x;
int x,y;
int x = 450,y = -462;
```
  
- #### 浮点类型
  - 浮点类型表示有小数部分的数字。Java语言中浮点类型分为**单精度浮点类型（float）**和**双精度浮点类型（double）**
  - 在默认情况下，小数都被看作double型，若使用float型小数，则需要在小数后面添加F或f。可以使用后缀d或D来明确表明这是一个double类型数据，不加d不会出错，**但声明float型变量时如果不加f**，系统会认为变量是double类型，从而出错。
- 实例代码
```
float f1 = 13.23f;
double d1 = 4562.12d;
double d2 = 45678.1564;
```
- #### 字符类型
  -  char型
字符类型（char）用于存储单个字符，占用16位（两个字节）的内存空间。在定义字符型变量时，要以单引号表示，如''**单引号**表示一个字符，而""**双引号**则表示一个字符串，虽然只有一个字符，但由于使用双引号，它仍然表示字符串，而不是字符。
- 实例代码
```
public class Gess {
    public static void main(String[] args) {
        char word = 'd', word2 = '@';
        int p = 23045, p2 = 45213;
        System.out.println("d在unicode表中的顺序位置是:" + (int) word);
        System.out.println("@在unicode表中的顺序位置是:" + (int) word2);
        System.out.println("unicode表中的第23045位是:" + (char) p);
        System.out.println("unicode表中的第45213位是:" + (char) p2);
    }
}
```
- 转义字符
  - 转义字符是一种特殊的字符变量，**它以反斜杠“\”开头，后跟一个或多个字符**。转义字符具有特定的含义，不同于字符原有的意义，故称“转义”。例如，printf函数的格式串中用到的“\n”就是一个转义字符，意思是“回车换行”。
 
![](/Java/pic/java2.png)
- 实例代码
```
char c1 = '\\';
char char1='\u2605';
System.out.println(c1);
System.out,println(char1);
```
- #### 布尔类型
  - 布尔类型又称逻辑类型，**通过关键字boolean来定义布尔类型变量，只有true和false两个值，分别代表布尔逻辑中的“真”和“假”**。布尔值不能与整数类型进行转换。布尔类型通常被用在**流程控制**中，作为判断条件。
- 实例代码
```
boolean b;
boolean b1,b2;
boolean b = true;
```

### 变量与常量
在程序执行过程中，其值不能被改变的量称为**常量**，其值能被改变的量称为**变量**。
- #### 标识符和关键字
  - 标识符可以简单地理解为一个名字，用来标识类名、变量名、方法名、数组名、文件名的有效字符序列。
  - 标识符由任意顺序的`字母`、`下画线（_）`、`美元符号（$）`和`数字`组成，并且**第一个字符不能是数字**。标识符不能是Java中的保留关键字。
  - 关键字是Java语言中已经被赋予特定意义的一些单词，不可以把这些字作为标
识符来使用。
![](/Java/pic/java3.png)

- #### 声明变量
  - 内存空间内的值就是变量值。在声明变量时可以是没有赋值，
也可以是直接赋给初值。
```
int age;
char char1='r';
```
 - 系统的内存可大略分为3个区域，即**系统（OS）区、程序（Program）区和数据（Data）区**
![](/Java/pic/java4.png)
- 常量称为**final变量**，在程序运算中只赋值一次
- 在程序中，一般会根据变量的“有效范围”将变量分为“成员变量”和“局部变量”。
  - **成员变量**：在类体中所定义的变量被称为成员变量，成员变量在整个类中都有效。类的成员变量又可分为两种，即**静态变量**和**实例变量**。
  - **局部变量**：在类的方法体中定义的变量（方法内部定义，“{”与“}”之间的代码中声明
的变量）称为局部变量。
![](/Java/pic/java5.png)

### 运算符
- #### 赋值运算法
  - 赋值运算符以符号“=”表示，它是一个二元运算符（对两个操作数作处理），
其功能是将右方操作数所含的值赋给左方的操作数。
- #### 算术运算符
  - Java中的算术运算符主要有`+（加）`、`-（减）`、`*（乘）`、`/（除）`、`%（求余）`，它们都是二元运算符。“+”和“-”运算符还可以作为数据的正负符号。
- #### 自增和自减运算符
  - 自增、自减运算符是**单目运算符**，可以放在操作元之前，也可以放在操作元之
后。操作元必须是一个整型或浮点型变量。自增、自减运算符的作用是使变量的值
**增1或减1**
```
++a(--a)    //表示在使用变量a之前，先将a值加(减)1   
a++(a--)    //表示在使用变量a之后，再将a值加(减)1
```    
若a++和++a独行来算，都相当于a=a+1
- #### 比较运算符
  - 比较运算符属于**二元运算符**，用于程序中的**变量之间、变量和自变量之间以及
其他类型的信息之间的比较**。比较运算符的运算结果是`boolean`型。当运算符对应
的关系成立时，运算结果为true，否则为false。
![](/Java/pic/java6.png)
- #### 逻辑运算符
  - 返回类型为布尔值的表达式，如比较运算符，可以被组合在一起构成一个更复
杂的表达式。这是通过逻辑运算符来实现的。逻辑运算符包括`&（&&）`（逻辑与）、
`||`（逻辑或）、`!`（逻辑非）。逻辑运算符的操作元必须是boolean型数据。
在逻辑运算符中，除了“！”是一元运算符之外，其他都是二元运算符。
![](/Java/pic/java7.png)
- #### 位运算符
  - 位运算符除“按位与”和“按位或”运算符外，其他只能用于处理整数的操作数。
  - 左边最高位是符号位，最高位是0表示正数，若为1则表示负数。负数采用补码表示，如-8的二进制表示为`111111111 111111111 1111111 11111000`。
- “按位与”运算
  - “按位与”运算的运算符为`“&”`，为双目运算符。“按位与”运算的运算法则是：如果两个整型数据a、b对应位都是1，则结果位才是1，否则为0。如果两个操作数的精度不同，则结果的精度与精度高的操作数相同  
- “按位或”运算
  - “按位或”运算的运算符为`“|”`，为双目运算符。“按位或”运算的运算法则是：如果两个操作数对应位都是0，则结果位才是0，否则为1。如果两个操作数的精度不同，则结果的精度与精度高的操作数相同。
  ![](/Java/pic/java8.png)
- “按位取反”运算
  - “按位取反”运算也称“按位非”运算,运算符为`“~”`，为单目运算符。“按位取反”就是将操作数二进制中的1修改为0，0修改为1。
- 按位异或”运算
  - “按位异或”运算的运算符是`“^”`，为双目运算符。“按位异或”运算的运算法则是：当两个操作数的二进制表示相同（同时为0或同时为1）时，结果为0，否则为1。若两个操作数的精度不同，则结果数的精度与精度高的操作数相同
### 三元运算符(条件运算符)
( ? : ) 该运算符有3个操作数，并且需要判断布尔表达式的值。并且决定哪个值应该赋值给变量。
```
x = (expression) ? value1 if true: value2 if false //expression表达式，value1为若前面成立则赋值给x，否则赋值value2给x。
```
三元运算符的运算规则为：若条件式的值为true，则整个表达式取值1，否则取值2。
三元运算符等价于`if…else语句`。
### 运算符优先级
运算符的优先级决定了表达式中运算执行的先后顺序。通常优先级由高到低的顺序依次是：
`增量和减量运算`。
`算术运算`。
`比较运算`。
`逻辑运算`。
`赋值运算`。
如果两个运算有相同的优先级，那么左边的表达式要比右边的表达式先被处理。
![](/Java/pic/java9.png)
### 数据类型转换
如果从低精度数据类型向高精度数据类型转换，则永远不会溢出，并且总是成功的；而把高精度数据类型向低精度数据类型转换时，则会有信息丢失，有可能失败。
数据类型转换有两种方式，即`隐式转换`与`显式转换`。\
- #### 隐式类型转换
  - 从**低级类型向高级类型的转换**，系统将自动执行，程序员无须进行任何操作。
这种类型的转换称为隐式转换。下列基本数据类型会涉及数据转换，不包括逻辑类
型和字符类型。这些类型按精度从`低到高`排列的顺序为byte < short < int <
long < float < double。
- #### 显式类型转换
  - 当把**高精度的变量的值赋给低精度**的变量时，必须使用显式类型转换运算（又
称强制类型转换）。 
  - 执行显式类型转换时，可能会导致精度损失。除boolean类型以外其他基本类
型，都能以显式类型的方法实现转换。
### 代码注释与编码规范
Java语言提供了3种添加注释的方法，分别为`单行注释`、`多行注释`和`文档注释`。
- #### 单行注释
  - “//”为单行注释标记，从符号“//”开始直到换行为止的所有内容均作为注
释而被编译器忽略。
语法如下：
//注释内容
例如，以下代码为声明的int型变量添加注释：
int age ; //定义int型变量用于保存年龄信息
- #### 多行注释
  - “/* */”为多行注释标记，符号“/*”与“*/”之间的所有内容均为注释内
容。注释中的内容可以换行。
语法如下：
/* 注释内容1 注释内容2 … */
注意
在多行注释中可嵌套单行注释。例如：
/* 程序名称：Hello world //开发时间：2008-03-05 */
注意
但在多行注释中不可以嵌套多行注释，以下代码为非法：
/* 程序名称：Hello world /*开发时间：2008-03-05 作者：张先生 */ */
- #### 文档注释
  - “/** */”为文档注释标记。符号“/**”与“*/”之间的内容均为文档注释
内容。当文档注释出现在声明（如类的声明、类的成员变量的声明、类的成员方法
声明等）之前时，会被Javadoc文档工具读取作为Javadoc文档内容。文档注释的格
式与多行注释的格式相同。
### 流程控制
- #### 复合语句
  - Java语言的复合语句是以整个块区为单位的语句，所以又称**块语句**。复合语句由开括号“{”开始，闭括号“}”结束
  - 类体就是以“{ }”作为开始与结束的标记，方法体同样也是以“{ }”作为标记。
复合语句中的每个语句都是从上到下被执行。复合语句以整个块为单位，能够用在任何一个单独语句可以用到的地方，并且在复合语句中还可以嵌套复合语句。
- 实例代码
```
public class Compound {
    public static void main(String[] args) {
        int x=20;
        {
            int y=40;
            System.out.println(y);
            int z=245;
            boolean b;
            {
                b=y>z;
                System.out.println(b);
            }
        }
        String word="hello java";
        System.out.println(word);
    }
}
```
- #### 条件语句
  - 条件语句可根据不同的条件执行不同的语句。条件语句包括**if条件语句**与
**switch多分支语句**。
- ##### if条件语句
  - 使用if条件语句，可选择是否要执行紧跟在条件之后的那个语句。关键字if之后是作为条件的“布尔表达式”，如果该表达式返回的结果为true，则执行其后的语句；若为false，则不执行if条件之后的语句。if条件语句可分为简单的**if条件语句、if…else语句和if…else if多分支语句**。
1. **简单的if条件语句**
   1. 布尔表达式：必要参数，表示最后返回的结果必须是一个布尔值。它可以是一个单纯的布尔变量或常量，也可以是使用关系或布尔运算符的表达式。
   2. 语句序列：可选参数。可以是一条或多条语句，当表达式的值为true时执行这些语句。若语句序列中仅有一条语句，则可以省略条件语句中的“{ } 
- 实例代码
```
public class Getif {
    public static void main(String[] args) {
       int x=40;
       int y=20;
       boolean b=x>y;
       if (b){
           System.out.println("x>y");
       }
       else {
           System.out.println("x<y");
       }
    }
 }  
```
2. **if…else语句**
   1. if后面“()”内的表达式的值必须是boolean型的。如果表达式的值为true，则执行紧跟if语句的复合语句；如果表达式的值为false，则执行else后面的复合语句。 
- 实例代码
```
public class Getifelse {
    public static void main(String[] args) {
        int math=100;
        int Russian=50;
        if (math>60){
            System.out.println("数学及格啦");
        }
        else{
            System.out.println("数学寄啦");
        }
        if (Russian>60){
            System.out.println("俄语及格啦");
        }
        else{
            System.out.println("俄语寄啦");
        }
    }
}
```
**if…else语句可以使用三元运算符进行简化。如下面的代码：**
```
if(a > 0) b = a;
 else b = -a;
```
3. **if…else if多分支语句**
   1. if…else if多分支语句用于针对某一事件的多种情况进行处理。通常表现
为“如果满足某种条件，就进行某种处理，否则如果满足另一种条件则执行另一种
处理”。
![](/Java/pic/java10.png)
- 实例代码
```
public class GetTerm {
    public static void main(String[] args) {
        int x=20;
        if (x>30){
            System.out.println("a的值大于30");
        }
        else if (x>10) {
            System.out.println("a的值大于10但小于30");
        }
        else if (x>0){
            System.out.println("a的值大于0但小于10");
        }
        else{
            System.out.println("a的值小于0");
        }
    }
}
```
- ##### switch多分支语句
  - 在编程中一个常见的问题就是检测一个变量是否符合某个条件，如果不符合，再用另一个值来检测，依此类推。当然，这种问题使用if条件语句也可以完成。
  - switch语句中表达式的值必须是**整型、字符型或字符串类型**，常量值1~n必须也是整型、字符型或字符串类型。**switch语句首先计算表达式的值，如果表达式的值和某个case后面的常量值相同，则执行该case语句后的若干个语句直到遇到break语句为止**。此时如果该case语句中没有break语句，将继续执行后面case中的若干个语句，直到遇到break语句为止。若没有一个常量的值与表达式的值相同，则执行default后面的语句。default语句为可选的，如果它不存在，且switch语句中表达式的值不与任何case的常量值相同，switch则不做任何处理。
- 实例代码
```
public class GetSwitch {
    public static void main(String[] args) {
        int week=3;
        switch (week){
            case 1:
                System.out.println("Monday");
            case 2:
                System.out.println("Tuesday");
            case 3:
                System.out.println("Wednesday");
                break;
            case 4:
                System.out.println("Thursday");
        }
    }
}
```
![](/Java/java11.png)
- #### 循环语句
  - 循环语句就是在满足一定条件的情况下反复执行某一个操作。在Java中提供了3
种常用的循环语句，分别是**while循环语句、do…while循环语句和for循环语句**
- ##### while循环语句
  - while语句也称条件判断语句，它的循环方式为利用一个条件来控制是否要继续
反复执行这个语句。
  - 当条件表达式的返回值为真时，则执行“{}”中的语句，当执行完“{}”中的语句后，重新判断条件表达式的返回值，直到表达式返回的结果为假时，退出循环。
- 实例代码
```
public class GetSum {
    public static void main(String[] args) {
        int x=1;
        int sum=0;
        while (x<=10){
            sum=sum+x;
            ++x;
            System.out.println("sum="+sum);
        }
    }
}
```
![](/Java/pic/java12.png)
- #### do…while循环语句
  - do…while循环语句与while循环语句类似，它们之间的区别是**while语句为先判断条件是否成立再执行循环体**，而**循环语句则先执行一次循环后，再判断条件是否成立**。也就是说，do…while循环语句中“{}”中的程序段至少要被执行一次。
 - 实例代码
```
  public class Cycle {
    public static void main(String[] args) {
        int a=100;
        while (a==60){
            System.out.println("ok1");
            a--;
        }
        int b=100;
        do {
            System.out.println("ok2");
            b--;
        }while (b==60);

    }
}
```
![](/Java/pic/java13.png)
- #### for循环语句
1. **for语句**
- 语法如下
```
for(表达式1;表达式2;表达式3){
  语句序列
}
```
其中：表达式1：初始化表达式，负责完成**变量的初始化**。
表达式2：循环条件表达式，**值为boolean型的表达式，指定循环条件**。
表达式3：循环后操作表达式，**负责修整变量，改变循环条件**。
- 实例代码
```
public class Circulate {
    public static void main(String[] args) {
        int sum=1;
        for (int i=1;i<=300;i+=2){
            if (i>=100)
                sum=sum+i;
        }
        System.out.println("100到300之间的所有偶数之和为："+sum);
    }
}
```
![](/Java/pic/java14.png)
2. **foreach语句**
foreach语句是for语句的特殊简化版本，不能完全取代for语句，但任何foreach语句都可以改写为for语句版本。foreach并不是一个关键字，习惯上将这种特殊的for语句格式称为foreach语句。
foreach语句中的元素变量x，不必对其进行初始化。下面通过简单的例子来介绍foreach语句是如何遍历一维数组的。
- 实例代码
```
public class Repetition {
    public static void main(String[] args) {
        int d[]={16,14,12,10,8,6,4};  //声明一维数组
        System.out.println("从16到4的偶数降序为：");  //输出信息
        for (int x:d){  //foreach语句，int x引用的变量，d指定要循环遍历的数组，最后将x输出
            System.out.println(x);
        }
    }
}
```
- #### 循环控制
- 循环控制包含两方面的内容，一方面是控制循环变量的变化方式，另一方面是控制循环的跳转。控制循环的跳转需要用到`break`和`continue`两个关键字，这两条跳转语句的跳转效果不同，break是**中断循环**，continue是**执行下一次循环**。
1. **break语句**
- 使用break语句可以跳出switch结构。在循环结构中，同样也可用break语句跳出当前循环体，从而中断当前循环。
- 实例代码
```
public class BreakTast {
    public static void main(String[] args) {
        for (int i=0;i<=10;i++){
            System.out.println(i);
            if (i==8){
                break;
            }
        }
        System.out.println("end");
    }
}
```
注意：**循环嵌套情况下**，break语句将只会使程序流程跳出包含它的最内层的循环结构，即**只跳出一层循环**。
- 实例代码
```
public class BreakInsideNested {
    public static void main(String[] args) {
        for (int i=0;i<3;i++){  //外部循环
            for (int j=0;j<6;j++){  //内部循环
                if (j==4){
                    break;
                }
                System.out.println("i="+i+"j="+j);
            }
        }
    }
}
```
外层循环不受任何影响，i最大值达2
- **如果想让break跳出外层循环，Java提供了“标签”的功能，语法如下：**
```
public static void main(String[] args) {
        Loop:for (int i=0;i<3;i++){
             for (int j=0;j<6;j++){
                 if (j==4){
                     break Loop;
                 }
                 System.out.println("i="+i+"j="+j);
             }
        }
    }
```
2. **continue语句**
- continue语句是针对break语句的补充。continue不是立即跳出循环体，而是跳过本次循环结束前的语句，回到循环的条件测试部分，重新开始执行循环。在for循环语句中遇到continue后，首先执行循环的增量部分，然后进行条件测试。在while和do…while循环中，continue语句使控制直接回到条件测试部分。
- 实例代码(输出1～20之间的奇数，使用continue跳出循环。)
```
public class ContinueTest {
    public static void main(String[] args) {
        for (int x=1;x<=20;x++){
            if (x%2==0){       //如果x是偶数
                continue;      //跳到下一循环
            }
            System.out.println(x); //输出i的值
        }
    }
}
```
### 字符串
- 字符串是Java程序中经常处理的对象，如果字符串运用得不好，将影响到程序运行的效率。在Java中字符串作为`String`类的实例来处理。


### 数组
- 数组是最为常见的一种数据结构，是**相同类型的用一个标识符封装到一起**的基本类型数据序列或对象序列。可以用一个统一的数组名和下标来唯一确定数组中的元素。实质上，数组是一个简单的线性序列
- #### 一维数组的创建及使用
  - 创建一维数组：数组作为对象允许使用new关键字进行内存分配。在使用数组之前，必须首先**定义数组变量所属的类型**。一维数组的创建有两种形式。
1. 先声明，再用new运算符进行内存分配
声明一维数组有下列两种方式：
```
数组元素类型 数组名字[]；
数组元素类型[] 数组名字；
```
- **数组元素类型**决定了**数组的数据类型**。它可以是Java中任意的数据类型，包括简单类型和组合类型。数组名字为一个合法的标识符，符号“[ ]”指明该变量是一个数组类型变量。**单个“[ ]”表示要创建的数组是一个一维数组**。
- 声明一维数组，实例代码如下：
```
int arr[];
String str[];
```
声明数组后，还不能立即访问它的任何元素，因为声明数组只是给出了数组名字和元素的数据类型，要想真正使用数组，还要为它分配内存空间。在为数组分配内存空间时必须指明数组的长度。为数组分配内存空间的语法格式如下：
- 数组名字 = new 数组元素的类型[数组元素的个数];
  - 数组名字：被连接到数组变量的名称。
  - 数组元素的个数：指定数组中变量的个数，即数组的长度。
  - 通过上面的语法可知，使用new关键字分配数组时，必须指定数组元素的类型和数组元素的个数，即数组的长度。
2. 声明的同时为数组分配内存
这种创建数组的方法是将数组的声明和内存的分配合在一起执行。
- 语法如下：
- 数组元素的类型 数组名 = new数组元素的类型[**数组元素的个数**];
- #### 初始化一维数组
- 数组与基本数据类型一样可以进行初始化操作。数组的初始化可分别初始化数
组中的每个元素。数组的初始化有以下两种形式：
```
int x[]=new int[]{1,2,6,74};
int x[]={123,324,435};
```
- #### 二维数组的创建及使用
- 如果一维数组中的各个元素仍然是一个组，那么它就是一个二维数组。二维数组常用于表示表，表中的信息以行和列的形式组织，第个一下标代表元素所在的行，第二个下标代表元素所在的列。
- **二维数组的创建**
1. **先声明，再用`new`运算符进行内存分配**
声明二维数组的语法如下：
- 数组元素的类型 数组名字[ ][ ]; 数组元素的类型[ ][ ] 数组名字;
- 例:int myarr[][];
2. **声明的同时为数组分配内存**
- 第二种方式同第一种实现的功能相同。使用这种方式为二维数组分配内存时，
首先指定**最左边维数的内存**，然后**单独地给余下的维数分配内存**。通过第二种方式为二维数组分配内存。
![](/Java/pic/java15.png)
- #### 二维数组初始化
- 二维数组的初始化与一维数组初始化类似,同样可以使用大括号完成。
- 语法如下：
- type arrayname[][] = {value1,value2…valuen};
  - type：数组数据类型。
  - arrayname：数组名称，一个合法的标识符。
  - value：数组中各元素的值。
- #### 数组的基本操作
- 遍历数组
  - 遍历数组就是**获取数组中的每个元素**。通常遍历数组都是使用`for循环`来实现。
  遍历一维数组很简单，也很好理解，下面详细介绍遍历二维数组的方法。
  **遍历二维数组需使用双层for循环**，通过数组的`length`属性可获得数组的长度。
- 填充替换数组元素
  - 数组中的元素定义完成后，可通过`Arrays`类的静态方法`fill()`来对数组中的元素进行替换。该方法通过各种重载形式可完成对任意类型的数组元素的替换。
- fill()方法有两种参数类型，下面以int型数组为例介绍fill()方法的使用方法。 
1. **fill(int[] a,int value)**
该方法可将指定的int值分配给int型数组的每个元素。
- 语法如下：
  - fill(int[] a,int value)
  - a：要进行元素替换的数组。
  - value：要存储数组中所有元素的值。
2. **fill(int[] a,int fromIndex,int toIndex,int value)**
该方法将指定的int值分配给int型数组指定范围中的每个元素。填充的范围从索fromIndex（包括）一直到索引toIndex（不包括）。如果fromIndex ==
toIndex，则填充范围为空。
- 语法如下：
- fill(int[] a,int fromIndex,int toIndex,int value)
  - a：要进行填充的数组。
  - fromIndex：要使用指定值填充的第一个元素的索引（包括）。
  - toIndex：要使用指定值填充的最后一个元素的索引（不包括）。
  - value：要存储在数组所有元素中的值。
- #### 对数组进行排序
  - 通过`Arrays`类的静态`sort()`方法可以实现对数组的排序。sort()方法提供了多种重载形式，可对任意类型的数组进行升序排序。
- #### 复制数组
  - `Arrays`类的`copyOf()`方法与`copyOfRange()`方法可以实现对数组的复制。`copyOf()`方法是**复制数组至指定长度**，`copyOfRange()`方法则将**指定数组的指定长度复制到一个新数组中**。
1. `copyOf()`方法
该方法提供了多种重载形式，用于满足不同类型数组的复制。
- 语法如下：
- copyOf(arr,int newlength)
  - arr：要进行复制的数组。
  - newlength：int型常量，指复制后的新数组的长度。**如果新数组的长度大于数组arr的长度，则用0填充**（根据复制数组的类型来决定填充的值，**整型数组用0填充，char型数组则使用null来填充**）；**如果复制后的数组长度小于数组arr的长度，则会从数组arr的第一个元素开始截取至满足新数组长度为止**。
2. `copyOfRange()`方法
该方法同样提供了多种重载形式。
- 语法如下：
- copyOfRange(arr,int formIndex,int toIndex)
  - arr：要进行复制的数组对象。
  - formIndex：指定开始复制数组的索引位置。formIndex必须在0至整个数组的长度之间。新数组包括索引是formIndex的元素。
  - toIndex：要复制范围的最后索引位置。可大于数组arr的长度。新数组不包括索引是toIndex的元素。
- #### 数组查询
  - `Arrays`类的`binarySearch()`方法，可使用二分搜索法来搜索指定数组，以获得指定对象。该方法返回要搜索元素的索引值。binarySearch()方法提供了多种重载形式，用于满足各种类型数组的查找需要。binarySearch()方法有两种参数类型。
1. `binarySearch(Object[],Object key)`
- 语法如下：
- binarySearch(Object[] a,Object key)
  - a：要搜索的数组。
  - key：要搜索的值。
- 实例代码:
```
import java.util.Arrays;
public class Reference {
    public static void main(String[] args) {
        int ia[]=new int[]{1,8,9,4,5};
        Arrays.sort(ia); //对数组从小到大进行排序(Arrays的方法sort)
        int index=Arrays.binarySearch(ia,4);
        System.out.println("4的索引位置是:"+index);
    }
}
```
2. `binarySearch(Object[],int fromIndex,int toIndex,Object
key)`该方法在指定的范围内检索某一元素。
- 语法如下：
- binarySearch(Object[] a,int fromIndex,int toIndex,Object key)
  - a：要进行检索的数组。
  - fromIndex：指定范围的开始处索引（包含）。
  - toIndex：指定范围的结束处索引（不包含）。
  - key：要搜索的元素。
在使用该方法之前同样要对数组进行排序，来获得准确的索引值。如果要搜索的元素key在指定的范围内，则返回搜索键的索引；否则返回-1或“-”（插入点）。如果范围中的所有元素都小于指定的键，则为toIndex（注意，这保证了当且仅当此键被找到时，返回的值将大于等于0）。
- 实例代码:
```
import java.util.Arrays;

public class Rakel {
    public static void main(String[] args) {
        String b[]=new String[]{"ab","cd","ef","yz"};
        Arrays.sort(b); //对数组从小到大进行排序(Arrays的方法sort)
        int x=Arrays.binarySearch(b,0,2,"cd");
        System.out.println("cd的索引位置为:"+x);
    }
}
```
- ### 数组排序算法
- #### 冒泡排序
  - 冒泡排序的基本思想是**对比相邻的元素值**，如果满足条件就交换元素值，**把较小的元素移动到数组前面，把大的元素移动到数组后面**（也就是交换两个元素的位置），这样较小的元素就像气泡一样从底部上升到顶部。
- 冒泡算法由**双层循环**实现，其中**外层循环用于控制排序轮数**，一般为要排序的
数组长度减1次，因为最后一次循环只剩下一个数组元素，不需要对比，同时数组已
经完成排序了。而**内层循环主要用于对比数组中每个邻近元素的大小**，以确定是否
交换位置，对比和交换次数随排序轮数而减少。
![](/Java/pic/java16.png)
- 实例代码:
```
public class BubbleSort {
    public static void main(String[] args) {
        //创建一个乱序的数组元素
        int[] array={34,45,89,12,23,54,75};
        //创建冒泡排序类的对象
        BubbleSort sorter=new BubbleSort();
        //调用排序方法将数组排序
        sorter.sort(array);
    }
    /**
     *
     * @param array//要排序的数组
     *
     */
    public void sort(int[]array){
        for (int i=1;i<array.length;i++){
            //比较相邻两个元素，较大的数往后冒泡
            for (int j=0;j<array.length-i;j++){
                if (array[j] > array[j+1]){
                    int temp=array[j];//把第一个元素值保存到临时变量中
                    array[j]=array[j+1];//把第二个元素值保存到第一个元素单元中
                    array[j+1]=temp;//把临时变量（也就是第一个元素原值）保存到第二个元素中
                }
            }
        }
        showArray(array); //输出冒泡排序后的数组元素
    }
    /**
     * //显示数组中的所有元素
     * @param array
     *
     */
    public void showArray(int[]array){
        for (int i:array){ //遍历数组
            System.out.print(">"+i); //输出每个数组元素值
        }
        System.out.println();
    }
}
```
- #### 直接选择排序
  - 直接选择排序方法属于选择排序的一种，它的排序速度要比冒泡排序快一些，也是常用的排序算法
  - 直接选择排序的基本思想是将指定排序位置与其他数组元素分别对比，如果满足条件就交换元素值。注意这里与冒泡排序的区别，不是交换相邻元素，而是**把满足条件的元素与指定的排序位置交换**（如从最后一个元素开始排序），**这样排序好的位置逐渐扩大，最后整个数组都成为已排序好的格式**。
  - 实例代码:
```
/**
 *
 *
 *
 */
public class Selectsort {
    public static void main(String[] args) {
        int[]array={1,32,45,36,67,89,12};
        Selectsort sorter=new Selectsort();
        sorter.sort(array);
    }
    /**
     *
     * @param array
     *
     */
    public void sort(int[]array){ //调用上面sort方法及其变量
        int index;
        for (int i=1;i<=array.length;i++){
            index=0;
            for (int j=1;j<=array.length-i;j++){
                if (array[j]>array[index]){
                    index=j;
                }
            }
            int temp=array[array.length-i];
            array[array.length-i]=array[index];
            array[index]=temp;
        }
        showArray(array);
    }
    /**
     *
     *
     * @param array
     *
     */
    public void showArray(int[]array){
        for (int i:array){
            System.out.print(">"+i);;
        }
        System.out.println();
    }
}
```
- #### 反转排序
  - 反转排序就是以相反的顺序把原有数组的内容重新排序。
  - 反转排序的基本思想比较简单，也很好理解，其实现思路就是把数组最后一个元素与第一个元素替换，倒数第二个元素与第二个元素替换，依此类推，直到把所有数组元素反转替换。
  - 实例代码:
```
/**
 *
 *
 *
 */
public class ReverseSort {
    public static void main(String[] args) {
        int[] array={13,20,32,56,78,90};
        ReverseSort sorter=new ReverseSort();
        sorter.sort(array);
    }
    /**
     *
     * @param array
     * 要排序的数组
     */
    public void sort(int[]array) {
        System.out.println("数组原有内容:");
        showArray(array);
        int temp;
        int len=array.length;
        for (int i=0;i<len/2;i++){
            temp=array[i];
            array[i]=array[len-1-i];
            array[len-1-i]=temp;
        }
        System.out.println("数组反转后内容:");
        showArray(array);
    }
    /**
     *
     *
     * @param array
     * 要显示的数组
     */
    public void showArray(int[]array){
        for (int i:array){
            System.out.println("\t"+i);
        }
        System.out.println();
    }
}
```
- ### 类和对象
- #### 类
  - 类是**封装对象的属性和行为的载体**，而在Java语言中对象的属性以**成员变量**的形式存在，对象的方法以**成员方法**的形式存在。
- **成员变量**
- 为了了解成员变量，首先定义一个图书类，成员变量对应于类对象的属性，在Book类中设置3个成员变量，分别为id、name和category，分别对应于图书编号、图书名称和图书类别3个图书属性。
- 实例代码:
```
public class book {
    private String name; //定义成员变量

    public String getName(){ //定义成员方法
        int id=0; //定义局部变量
        setName("Java");
        return id+this.name; 
    }
    private void setName(String name){ //定义一个setName()成员方法
        this.name=name;
    }
    public book getbook(){
        return this;
    }
}
```
- **成员方法**
- 定义成员方法的语法格式如下：
```
权限修饰符 返回值类型 方法名(参数类型 参数名){
  ...//方法体
  return 返回值；
}  
```
- 一个成员方法可以有参数，这个参数可以是**对象**，也可以是**基本数据类型的变量**，同时成员方法有返回值和不返回任何值的选择，如果方法需要返回值，可以在方法体中使用`return`关键字，使用这个关键字后，方法的执行将被终止
- **权限修饰符**
  - Java中的权限修饰符主要包括`private`、`public`和`protected`，这些修饰符控制着对类和类的成员变量以及成员方法的访问。如果一个类的成员变量或成员方法被修饰为`private`，则该成员变量**只能在本类中被使用**，在**子类中是不可见的**，并且对其他包的类也是不可见的。如果将类的成员变量和成员方法的访问权限设置为`public`，那么除了可以在**本类使用这些数据之外，还可以在子类和其他包的类中使用**。如果一个类的访问权限被设置为`private`，**这个类将隐藏其内的所有数据，以免用户直接访问它**。如果需要使类中的数据被子类或其他包中的类使用，可以将这个类设置为`public`访问权限。如果一个类使用`protected`修饰符，那么只有本包内的该类的子类或其他类可以访问此类中的成员变量和成员方法。
- **局部变量**
  - 如果在成员方法内定义一个变量，那么这个变量被称为局部变量。
- **局部变量的有效范围**
  - 可以将局部变量的有效范围称为**变量的作用域**，局部变量的有效范围从该变量的声明开始到该变量的结束为止。
![](/Java/pic/java17.png)
- **`this`关键字**
  - 使用this关键字来代表本类对象的引用，this关键字被隐式地用于引用对象的成员变量和方法
  - 事实上，this引用的就是本类的一个对象。在局部变量或方法参数覆盖了成员变量时，如上面代码的情况，就要添加this关键字明确引用的是类成员还是局部变量或方法参数。
- **类的构造方法**
  - 在类中除了成员方法之外，还存在一种特殊类型的方法，那就是构造方法。构造方法是一个与类同名的方法，对象的创建就是通过构造方法完成的。每当类实例化一个对象时，类都会自动调用构造方法。
  - 构造方法**没有返回值**。
  - 构造方法的名称要与**本类的名称相同**。
- #### 静态变量、常量和方法
  - 由`static`修饰的变量、常量和方法被称作静态变量、常量和方法。
  - 被声明为`static`的变量、常量和方法被称为静态成员。静态成员属于类所有，区别于个别对象，可以在本类或其他类使用类名和“.”运算符调用静态成员。
- 对于静态方法(使用规则):
  - 在静态方法中不可以使用`this`关键字。
  - 在静态方法中不可以直接**调用非静态方法**。 
- 调用静态常量，变量以及方法的实例代码:
```
public class StaticTest {
    static double PI=3.1456; //定义静态常量
    static int id; //定义静态变量

    public static void Method1(){ //在类中定义静态方法

    }
    public void Method2(){ //在类中定义一个非静态方法
        System.out.println(StaticTest.PI); //调用静态常量
        System.out.println(StaticTest.id); //调用静态变量
        StaticTest.Method1(); //调用静态方法
    }
}
```  
- #### 类的主方法
- 在主方法的定义中可以看到其具有以下特性：
  - **主方法是静态的**，所以如要直接在主方法中**调用其他方法，则该方法必须也是静态的**。
  - 主方法**没有返回值**。
  - 主方法的形参为数组。其中args[0]~args[n]分别代表程序的第一个参数到第n个参数，可以使用`args.length`获取**参数的个数**。
- #### 对象
- **对象的创建**
  - 准确地说，可以在Java语言中使用`new`操作符**调用构造方法创建对象**。
![](/Java/pic/java18.png)
- **访问对象的属性和行为**
- 如果希望成员变量不被其中任何一个对象改变，可以使用`static`关键字。
- 实例代码：
```
public class AccessProperty {
    static int i=47; //定义静态成员变量
    public void call(){ //定义成员方法
        System.out.println("调用call()方法");
        for(i=0;i<3;i++){
            System.out.print(i+"");
            if (i==2){
                System.out.println("\n");
            }
        }
    }
    public AccessProperty(){ //定义构造方法
    }
    public static void main(String[] args) { //定义主方法
        AccessProperty t1=new AccessProperty(); //创建一个对象
        AccessProperty t2=new AccessProperty(); //创建另一个对象
        t2.i=60;
        //使用第一个对象调用类成员变量
        System.out.println("第一个实例对象调用i变量的结果为:"+t1.i++);
        t1.call();//使用第一个对象调用类成员方法
        //使用第二个对象调用类成员变量
        System.out.println("第二个实例对象调用i变量的结果为:"+t2.i);
        t2.call();//使用第二个对象调用类成员方法
    }
}
```
![](/Java/pic/java19.png)
从上述运行结果中可以看到，**由于使用t2.i=60语句改变了静态成员变量的值，使用对象t1调用成员变量的值也为60**，这正是**i值被定义为静态成员变量的效果**，即使使用两个对象对同一个静态成员变量进行操作，依然可以改变静态成员变量的值，因为在内存中两个对象同时指向同一块内存区域。`t1.i++`语句执行完毕后，i值变为3。当再次调用`call()`方法时又被重新赋值为0，做循环打印操作。
- #### 对象的引用
  - 类名 对象引用名称
  - 引用与对象相关联的语法如下：
  - `Book book=new Book();`
- #### 对象的比较
  - 在Java语言中有两种比较对象的方式，分别为`“==”`运算符与`equals()`方法。
- 实例代码:
```
public class Compare {
    public static void main(String[] args) {
        String c1=new String("abc"); //创建两个String型对象引用
        String c2=new String("abc");
        String c3=c1; //将c1对象引用赋予c3
        System.out.println("c2==c3的运算结果为:"+(c2==c3));
        System.out.println("c2.equals(c3)的运算结果为:"+(c2.equals(c3)));
    }
}
```
- 第一个:false 第二个:true
- 从上述运行结果中可以看出，`“==”`运算符和`equals()`方法比较的内容是不相同的，`equals()`方法是`String`类中的方法，它**用于比较两个对象引用所指的内容是否相等**；而`“==”`运算符比较的是**两个对象引用的地址是否相等**。由于c1与c2是两个不同的对象引用，两者在内存中的位置不同，而`“String c3=c1;”`语句将c1的
引用赋给c3，所以c1与c3这两个对象引用是相等的，也就是打印c1==c3这样的语句将返回true值。
- ### 包装类
- #### Integer
  - `java.lang`包中的`Integer`类、`Long`类和`Short`类，可将基本类型`int、long`和`short`封装成一个类。
  - 该类提供了多个方法，能在int类型和`String`类型之间互相转换，同时还提供了其他一些处理int类型时非常有用的常量和方法。
- *构造方法*
  - `Integer (int number)`
    - 该方法以一个`int`型变量为参数来获取`Integer`对象
    - 例：`Integer number = new Integer(7);`
  - `Integer (String str)`
    - 该方法以一个`String`型变量为参数来获取`Integer`对象。
    - 例：`Integer number = new Integer("45");`
![](/Java/pic/java20.png)
- `Integer`类中的`parseInt()`方法返回与调用该方法的数值字符串相应的整型
`（int）`值。
- `Integer`类中的`parseInt()`方法返回与调用该方法的数值字符串相应的整型`（int）`值。
- 实例代码:
```
public class Summation {
    public static void main(String[] args) {
        String str[]={"23","43","56","67","78"};
        int sum=0;
        for (int i=0;i<str.length;i++){
            int myint=Integer.parseInt(str[i]); //将数组中每个元素转换为int型
            sum=sum+myint; //叠加
        }
        System.out.println("数组的元素之和为："+sum);
    }
}
```
|方法|字符串类别|
|:----:|:----:|
|toString()|十进制字符串|
|toBinaryString()|二进制字符串|
|toHexString()|十六进制字符串|
|toOctalString()|八进制字符串|
- 实例代码:
```
ublic class Charac {
    public static void main(String[] args) {
        String str=Integer.toString(123);
        String str2=Integer.toBinaryString(123);
        String str3=Integer.toHexString(123);
        String str4=Integer.toOctalString(123);
        System.out.println("'123’的十进制表示为："+str);
        System.out.println("'123'的二进制表示为："+str2);
        System.out.println("'123'的十六进制表示为："+str3);
        System.out.println("'123'的八进制表示为："+str4);
    }
}
```
- **常量**
  - `MAX_VALUE`：表示int类型可取的最大值，即${2}^{31}$-1。
  - `MIN_VALUE`：表示int类型可取的最小值，即${-2}^{31}$。
  - `SIZE`：用来以二进制补码形式表示int值的位数。
  - `TYPE`：表示基本类型int的Class实例。 
- #### Boolean
  - 一个`Boolean`类型的对象只包含一个类型为`boolean`的字段。此外，此类还为`boolean`和`String`的相互转换提供了许多方法，并提供了处理`boolean`时非常有用的其他一些常量和方法。
- *构造方法*
  - `Boolean(boolean value)`
    - 该方法创建一个表示`value`参数的`Boolean`对象。
    - 例:`Boolean b = new Boolean(true);`
  - `Boolean(String str)`
    - 该方法以`String`变量作为参数创建`Boolean`对象。如果`String`参数不为`null`且在忽略大小写时等于true，则分配一个表示`true`值的Boolean对象，否则获得一个`false`值的Boolean对象。
    - 以String为变量，例:`Boolean bool = new Boolean("ok");`
![](/Java/pic/java21.png)
- #### Byte
  - 一个Byte类型的对象只包含一个类型为byte的字段。
  - 该类还为`byte`和`String`的相互转换提供了方法，并提供了其他一些处理byte时非常有用的常量和方法。
- *构造方法*
  - `Byte(byte value)` 
    - 通过这种方法创建的`Byte`对象，可表示指定的`byte`值。
    - 例:`byte mybyte = 45; Byte b = new Byte(mybyte);`
  - `Byte(String str)` 
    - 通过这种方法创建的`Byte`对象，可表示`String`参数所指示的`byte`值。
    - `Byte mybyte = new Byte("12");`
![](/Java/pic/java22.png)
- 常量同Integer型相同
- #### Character
  - `Character`类在对象中包装一个基本类型为`char`的值。一个Character类型的对象包含类型为char的单个字段。
- *构造方法*
  - `Character(char value)`
  - 该类的构造函数必须是一个`char`类型的数据。通过该构造函数创建的`Character`类对象包含由char类型参数提供的值。一旦Character类被创建，它包含的数值就不能改变了。
  - 例:`Character mychar = new Character('s');`
![](/Java/pic/java23.png)
- *常量*
  - `CONNECTOR_PUNCTUATION`：返回byte型值，表示`Unicode`规范中的常规类别`“Pc”`。
  - `TITLECASE_LETTER`：返回`byte`型值，表示`Unicode`规范中的常规类别`“Lt”`。
  - `UNASSIGNED`：返回`byte`型值，表示`Unicode`规范中的常规类别`“Cn”`。

- #### Double
  - `Double`和`Float`包装类是对`double、float`基本类型的封装，它们都是`Number`类的子类，又都是对**小数**进行操作，所以常用方法基本相同
- *构造方法*
  - `Double(double value)`：基于`double`参数创建`Double`类对象。
  - `Double(String str)`：构造一个新分配的`Double`对象，表示用字符串表示的`double`类型的浮点值。
![](/Java/pic/java24.png)
- `常量`
  - `MAX_EXPONENT`：返回`int`值，表示有限`double`变量可能**具有的最大指数**。
  - `MIN_EXPONENT`：返回`int`值，表示标准化`double`变量可能具有的最小指数。
  - `NEGATIVE_INFINITY`：返回`double`值，表示保存`double`类型的负无穷大值的常量。
  - `POSITIVE_INFINITY`：返回`double`值，表示保存`double`类型的正无穷大值的常量。

- #### Number
  - 抽象类`Number`是`BigDecimal`、`BigInteger`、`Byte`、`Double`、`Float`、`Integer`、`Long`和`Short`类的父类，`Number`的子类必须提供将表示的数值转换为`byte、double、float、int、long和short`的方法。
![](/Java/pic/java25.png)

- ### 数字处理类
  - Java提供了许多数字处理类，包括`DecimalFormat`类（用于格式化数字）、`Math`类（为各种数学计算提供了工具方法）、`Random`类（为处理随机数问题提供了各种方法）、`BigInteger`类与`BigDecimal`类（为所有大数字的处理提供了相应的数学运算操作方法）。
- #### 数字格式化
  - 数字格式化操作主要针对的是浮点型数据，包括`double`型和`float`型数据。在Java中使用`java.text.DecimalFormat`格式化数字
- 在Java中没有格式化的数据遵循以下原则：
  - 如果数据**绝对值大于0.001并且小于10000000**，使以常规小数形式表示。
  - 如果数据**绝对值小于0.001或者大于10000000**，使用科学记数法表示。
- `DecimalFormat`是`NumberFormat`的一个子类，用于*格式化十进制数字*。它可以将一些数字格式化为*整数、浮点数、百分数*等。通过使用该类可以为要输出的数字加上单位或控制数字的精度。一般情况下可以在实例化`DecimalFormat`对象时传递数字格式，也可以通过`DecimalFormat`类中的`applyPattern()`方法来实现数字格式化。
![](/Java/java26.png)

- #### 数学运算
  - 在Java语言中提供了一个执行数学基本运算的`Math`类，该类包括常用的数学运算方法，如三角函数方法、指数函数方法、对数函数方法、平方根函数方法等一些常用数学函数，除此之外还提供了一些常用的数学常量，如``PI、E`等。
- **常用数学运算方法** 
  - 在Math类中的常用数学运算方法较多，大致可以将其分为4大类别，分别为*三角函数方法*、*指数函数方法*、*取整函数方法*以及*取最大值、最小值和绝对值函数方法*。
    - **三角函数方法** 
      - `public static double sin(double a)`：返回角的三角正弦。
      - `public static double cos(double a)`：返回角的三角余弦。
      - `public static double tan(double a)`：返回角的三角正切。
      - `public static double asin(double a)`：返回一个值的反正弦。
      - `public static double acos(double a)`：返回一个值的反余弦。
      - ` public static double atan(double a)`：返回一个值的反正切。
      - `public static double toRadians(double angdeg)`：将角度转换为弧度。
      - `public static double toDegrees(double angrad)`：将弧度转换为角度。
      - 以上每个方法的参数和返回值都是`double`型的。将这些方法的参数的值设置为`double`型是有一定道理的，参数以弧度代替角度来实现，其中1°等于π/180弧度，所以180°可以使用π弧度来表示。除了可以获取角的正弦、余弦、正切、反正弦、反余弦、反正切之外，Math类还提供了**角度和弧度相互转换的方法**`toRadians()和toDegrees()`。但需要注意的是，角度与弧度的转换通常是不精确的。
    - **指数函数方法**
      - `public static double exp(double a)`：用于获取e的a次方，即取eª。
      - `public static double log(double a)`：用于取自然对数，即取lna的值。
      - `public static double log10(double a)`：用于取底数为10的对数。
      - `public static double sqrt(double a)`：用于取a的平方根，其中a的值不能为负值。
      - `public static double cbrt(double a)`：用于取a的立方根。
      - `public static double pow(double a,double b)`：用于取a的b次方。
    - **取整函数方法**
      - `public static double ceil(double a)`：返回大于等于参数的最小整数。
      - `public static double floor(double a)`：返回小于等于参数的最大整数。
      - `public static double rint(double a)`：返回与参数最接近的整数，如果两个同为整数且同样接近，则结果取偶数。
      - `public static int round(float a)`：将参数加上0.5后返回与参数最近的整数。
      - `public static long round(double a)`：将参数加上0.5后返回与参数最近的整数，然后强制转换为长整型。
    - **取最大值、最小值、绝对值函数方法**
      - `public static double max(double a,double b)`：取a与b之间的最大值。
      - `public static int min(int a,int b)`：取a与b之间的最小值，参数为整型。
      - `public static long min(long a,long b)`：取a与b之间的最小值，参数为长整型。
      - `public static float min(float a,float b)`：取a与b之间的最小值，参数为浮点型。
      - `public static double min(double a,double b)`：取a与b之间的最小值，参数为双精度型。
      - ` public static int abs(int a)`：返回整型参数的绝对值。
      - `public static long abs(long a)`：返回长整型参数的绝对值。
      - `public static float abs(float a)`：返回浮点型参数的绝对值。
      - `public static double abs(double a)`：返回双精度型参数的绝对值。
- #### 随机数
  - Java中主要提供了两种生成随机数的方式，分别为调用`Math`类的`random()`方法生成随机数和调用`Random`类生成各种数据类型的随机数。
- **Math.random()方法**
  - 在`Math`类中存在一个`random()`方法，用于产生随机数字。这个方法默认生成大于等于0.0且小于1.0的`double`型随机数，即`0<=Math.random()<1.0`。虽然`Math.random()`方法只可以产生0~1之间的`double`型数字，但只要在`Math.random()`语句上稍加处理，就可以使用这个方法产生任意范围的随机数
![](/Java/pic/java27.png)
- 实例代码:
```
public class MathRondom {
    /**
     *定義產生偶數的方法
     * @param num1 起始範圍參數
     * @param num2 終止範圍參數
     * @return 隨機的範圍内偶數
     */
    public static int GetEvenNum(double num1,double num2){
        int s=(int)num1+(int)(Math.random()*(num2-num1)); //大於等於num1而小於num2
        if (s%2==0){ //取餘為0
            return s;
        }else { //取餘不爲0，加1成偶數
            return s+1;
        }
    }
    public static void main(String[] args) { //輸出調用方法GetEvenNum
        System.out.println("任意一個2到64的偶數為:"+GetEvenNum(2,64));
    }
}
```
- 若要随即表达字符，则可用实例代码来表示:
`(char)(cha1+Math.random()*(cha2-cha1+1))`
(重点:该随机数表达范围为≥cha1而＜cha2)
- 实例代码:
```
public class MathRandomChar {
    public static char GetRandomchar(char cha1,char cha2){
        return(char)(cha1+Math.random()*(cha2-cha1+1));
    }
    public static void main(String[] args) {
        System.out.println("'a'到'z'字符之间任意一个:"+GetRandomchar('a','z'));
        System.out.println("'A'到'Z'字符之间任意一个:"+GetRandomchar('A','Z'));
        System.out.println("'0'到'9'数字字符之间任意一个:"+GetRandomchar('0','9'));
    }
}
```
- **Random类**
  - 除了`Math`类中的`random()`方法可以获取随机数之外，Java中还提供了一种可以获取随机数的方式，那就是`java.util.Random`类。通过**实例化**一个`Random`对象可以创建一个随机数生成器。 
  - 例:`Random r=new Random(); //定义一个随机数对象`
  - 在`Random`类中提供了获取各种数据类型随机数的方法:
    - `public int nextInt()`：返回一个随机整数。
    - `public int nextInt(int n)`：返回大于等于0且小于n的随机整数。
    - `public long nextLong()`：返回一个随机长整型值。
    - `public boolean nextBoolean()`：返回一个随机布尔型值。
    - `public float nextFloat()`：返回一个随机浮点型值。
    - `public double nextDouble()`：返回一个随机双精度型值。
    - `public double nextGaussian()`：返回一个概率密度为高斯分布的双精度值。
- **大数字运算**
  - 在Java中提供了大数字的操作类，即`java.math.BigInteger`类与`java.math.BigDecimal`类。这两个类用于高精度计算，其中`BigInteger`类是针对**大整数**的处理类，而`BigDecimal`类则是针对**大小数**的处理类。 
- **BigInteger**
  - `BigInteger`类型的数字范围较`Integer`类型的数字范围要大得多。前文介绍过`Integer`是int的包装类，int的最大值为${2}^{31}$-1，如果要计算更大的数字，使用Integer数据类型就无法实现了，所以Java中提供了`BigInteger`类来处理更大的数字。`BigInteger`支持**任意精度的整数**，也就是说，在运算中BigInteger类型可以准确地表示任何大小的整数值而不会丢失信息。
  - 除了基本的加、减、乘、除操作之外，还提供了**绝对值、相反数、最大公约数以及判断是否为质数**等操作。
  - BigInteger类中常用的几种运算方法。(**val是十进制字符串**)
    - `public BigInteger add(BigInteger val)`：做加法运算。
    - `public BigInteger subtract(BigInteger val)`：做减法运算。
    - `public BigInteger multiply(BigInteger val)`：做乘法运算。
    - `public BigInteger divide(BigInteger val)`：做除法运算。
    - `public BigInteger remainder(BigInteger val)`：做取余操作。
    - `public BigInteger[] divideAndRemainder(BigInteger val)`：用数组返回余数和商，结果数组中第一个值为商，第二个值为余数
    - `public BigInteger pow(int exponent)`：进行取参数的`exponent`次方操作。
    - `public BigInteger negate()`：取相反数。
    - `public BigInteger shiftLeft(int n)`：将数字左移n位，如果n为负数，做右移操作。
    - `public BigInteger shiftRight(int n)`：将数字右移n位，如果n为负数，做左移操作。
    - `public BigInteger and(BigInteger val)`：做与操作。
    - `public BigInteger or(BigInteger val)`：做或操作。
    - `public int compareTo(BigInteger val)`：做数字比较操作。
    - `public boolean equals(Object x)`：当参数x是BigInteger类型的数字并且数值相等时，返回`true`。
    - `public BigInteger min(BigInteger val)`：返回较小的数值。
    - `public BigInteger max(BigInteger val)`：返回较大的数值。
- **BigDecimal**
  - `BigDecimal`和`BigInteger`都能实现大数字的运算，不同的是`BigDecimal`加入了小数的概念。一般的`float`型和`double`型数据只可以用来做科学计算或工程计算，但由于在商业计算中要求数字精度比较高，所以要用到`java.math.BigDecimal`类。`BigDecimal`类支持任何精度的定点数，可以用它来精确计算货币值。
  - 在BigDecimal类中常用的两个构造方法如下。
    - `public BigDecimal(double val)`：实例化时将**双精度型**转换为`BigDecimal`类型。
    - `public BigDecimal(String val)`：实例化时将**字符串形式**转换为`BigDecimal`类型。
  - 下面列举了`BigDecimal`类中实现加、减、乘、除的方法。
    - `public BigDecimal add(BigDecimal augend)`：做加法操作。
    - `public BigDecimal subtract(BigDecimal subtrahend)`：做减法操作。
    - `public BigDecimal multiply(BigDecimal multiplicand)`：做乘法操作。
    - `public BigDecimal divide(BigDecimal divisor,int scale,introundingMode)`：做除法操作，方法中3个参数分别代表**除数**、**商的小数点后的位数**、**近似处理模式**。
![](/Java/pic/java28.png)
- 实例代码:
```
import java.math.BigDecimal;

public class BigDecimalDemo {
    static final int location=10;
    /**
     * 定义加法方法，参数为加数与被加数
     *
     * @param value1
     * 相加的第一个数
     * @param value2
     * 相加的第二个数
     * @return 两数之和
     */
    public BigDecimal add(double value1,double value2){
        BigDecimal b1=new BigDecimal(Double.toString(value1));
        BigDecimal b2=new BigDecimal(Double.toString(value2));
        return b1.add(b2);//调用加法方法
    }
    /**
     * 定义减法方法，参数为减数与被减数
     * @param value1 被减数
     *
     * @param value2 减数
     *
     * @return 两数之差
     */
    public BigDecimal sub(double value1,double value2){
        BigDecimal b1=new BigDecimal(Double.toString(value1));
        BigDecimal b2=new BigDecimal(Double.toString(value2));
        return b1.subtract(b2);//调用减法方法
    }
    /**
     * 定义乘法方法，参数为乘数与被乘数
     *
     * @param value1
     *      第一个乘数
     * @param value2
     *      第二个乘数
     * @return
     */
    public BigDecimal mul(double value1,double value2){
        BigDecimal b1=new BigDecimal(Double.toString(value1));
        BigDecimal b2=new BigDecimal(Double.toString(value2));
        return b1.multiply(b2); // 调用乘法方法
    }
    /**
     * 定义除法方法，参数为除数与被除数
     *
     * @param value1 被除数
     *
     * @param value2 除数
     *
     * @return
     *
     */
    public BigDecimal div(double value1,double value2){
        return div(value1,value2,location);//调用自定义除法方法
    }
    //定义除法方法，将参数分别位除数与被除数以及商小数点后的位数
    public BigDecimal div(double value1,double value2,int b){
        if (b<0){
            System.out.println("b的值必须大于等于0");
        }
        BigDecimal b1=new BigDecimal(Double.toString(value1));
        BigDecimal b2=new BigDecimal(Double.toString(value2));
        //调用除法方法，商小数点后保留b位，并将结果进行四舍五入操作
        return b1.divide(b2,b,BigDecimal.ROUND_HALF_UP);//调用除法方法
    }
    public static void main(String[] args) {
        BigDecimalDemo b=new BigDecimalDemo();
        System.out.println("两个数字相加的结果为:"+b.add(-8.0,9.4));
        System.out.println("两个数字相减的结果为:"+b.sub(-8.0,9.4));
        System.out.println("两个数字相乘的结果为:"+b.mul(-8.0,9.4));
        System.out.println("两个数字相除结果，结果小数后保留10位:"+b.div(10,2));
        System.out.println("两个数字相除,保留小数后5位:"+b.div(-8.0,9.4,5));
    }
}
```
### 类的高级特性
- #### 导入包
  - 使用`import`关键字导入包
    - import关键字的语法如下： 
```
import com.lzw.*; //指定com.lzw包中的所有类中的程序都能使用
import com.lzw.Math //指定com.lzw包中的Math类在程序中可以使用
```
- 在使用`import`关键字时，可以指定类的完整描述，如果为了使用包中更多的类，可以在使用`import`关键字指定时在包指定后加上*，这表示可以在程序中使用包中的所有类。
  - 使用import导入静态成员
    - 使用import导入静态成员的语法如下：
```
import static 静态成员
```
- 实例代码:
```
import static java.lang.Math.max;
import static java.lang.System.out;
public class ImportTest {
    public static void main(String[] args) {
        out.println("5和7比较大小:"+max(5,7));
    }
}
```
### 异常处理
- 异常分为两大类：已检查和未检查
  - 对于未检查异常也叫RunTimeException
![](/Java/pic/java34.png)
- #### 捕捉异常
  - Java语言的异常捕获结构由`try`、`catch`和`finally` 3部分组成。其中，`try`语句块存放的是可能发生异常的Java语句；`catch`程序块在`try`语句块之后，用来激发被捕获的异常；`finally`语句块是**异常处理结构的最后执行部分**，**无论`try`语句块中的代码如何退出**，都将执行`finally`语句块。
- **`try-each`语句**
- 实例代码：
```
public class Take {
    public static void main(String[] args) {
        try { //try语句中包含可能出现异常的程序代码
            String str = "Ally";
            System.out.println(str + "年龄是:");
            int age = Integer.parseInt("20L"); //数据类型转换
            System.out.println(age);
        } catch (Exception e) { //catch语句用来获取异常信息
            e.printStackTrace(); //输出异常性质
        }
        System.out.println("Program over");
    }
}
```
- 注意：
  - `Exception`是`try`代码块传递给catch代码块的变量类型，`e`是变量名。`catch`代码块中语句`“e.getMessage();”`用于输出错误性质。通常，异常处理常用以下3个函数来获取异常的有关信息。
    - `getMessage()`函数：输出错误性质.
    - `toString()`函数：给出异常的类型与性质。
    - `printStackTrace()`函数：指出异常的类型、性质、栈层次及出现在程序中的位置。
- **`finally`语句块**
  - 完整的异常处理语句一定要包含`finally`语句，无论程序中有无异常发生，并且无论之间的`try-catch`是否顺利执行完毕，都会执行`finally`语句。
- #### 常见异常
![](/Java/pic/java29.png)
- #### 自定义异常
  - 在程序中使用自定义异常类，大体可分为以下几个步骤：
    - 创建自定义异常类。
    - 在方法中通过`throw`关键字抛出异常对象。 
    - 如果在当前抛出异常的方法中处理异常，可以使用`try-catch`语句块捕获并处理，否则在方法的声明处通过`throws`关键字指明要抛出给方法调用者的异常，继续进行下一步操作。
    - 在出现异常方法的调用者中捕获并处理异常。
- 实例代码:
```
public class MyException extends Exception{
    public MyException(String ErrorMessage){
        super(ErrorMessage);
    }
}
public class Tran {
    static int avg(int number1,int number2)throws MyException{
        if (number1<0||number2<0){
            throw new MyException("不可以小于0");
        }
        if (number1>100||number2>100){
            throw new MyException("数值过于大了");
        }
        return (number1+number2)/2;
    }

    public static void main(String[] args) {
        try{
            int result=avg(-1,103);
            System.out.println(result);
        }catch (MyException e){
            System.out.println(e);
        }
    }
}
```
- 字符串`ErrorMessage`是要输出的错误信息。若想抛出用户自定义的异常对象，要使用`throw`关键字
- #### 在方法中抛出异常
  - 若某个方法可能会发生异常，但不想在当前方法中处理这个异常，则可以使用`throws`、`throw`关键字在方法中抛出异常。
- **使用`throws`关键字抛出异常**
- 实例代码:
```
public class Shoot {
    static void pop() throws NegativeArraySizeException{ //定义方法并抛出NegativeArraySizeException异常
        int arr[]=new int[-3]; //创建数组
    }

    public static void main(String[] args) {
        try { //try语句处理异常信息
            pop(); //调用pop()方法
        }catch (NegativeArraySizeException e){
            System.out.println("pop()方法抛出的异常");
        }
    }
}
```
- **使用`throw`关键字抛出异常**
  - `throw`关键字通常用于方法体中，并且抛出一个异常对象。程序在执行到`throw`语句时立即终止，它后面的语句都不执行。通过`throw`抛出异常后，如果想在上一级代码中来捕获并处理异常，则需要在抛出异常的方法中使用`throws`关键字在方法的声明中指明要抛出的异常；如果要捕捉`throw`抛出的异常，则必须使用`try-catch`语句块。
- 实例代码:
```
public class MyException2 extends Exception{ //创建自定义异常类
    String message; //定义String类型变量
    public MyException2(String ErrorMessage){ //父类方法
        message = ErrorMessage;
    }
    public String GetMessage(){ //覆盖父类方法
        return message;
    }
}
public class Captor {
    static int quotient(int x,int y)throws MyException2{ //定义方法中抛出异常
        if (y<0){ //判断参数是否小于0
            throw new MyException2("除数不能是负数"); //异常信息
        }
        return x/y; //返回值
    }

    public static void main(String[] args) {
        try {
            int result=quotient(4,-3);
        }catch (MyException2 e){
            System.out.println(e.GetMessage());
        }catch (ArithmeticException e){
            System.out.println("除数不能为0");
        }catch (Exception e){
            System.out.println("程序发生了其他的异常");
        }
    }
}
```
- #### 三种类型的异常处理
  - 声明异常
  - 抛出异常
  - 捕获异常
- #### 运行时异常
  - `RuntimeException`异常是程序运行过程中产生的异常。Java类库的每个包中都定义了异常类，所有这些类都是`Throwable`类的子类。`Throwable`类派生了两个子类，分别是`Exception`和`Error`类。`Error`类及其子类用来描述Java运行系统中的内部错误以及资源耗尽的错误，这类错误比较严重。`Exception`类称为**非致命性类**，可以通过捕捉处理使程序继续执行。`Exception`类又根据错误发生的原因分为`RuntimeException`异常和除`RuntimeException`之外的异常

- ### `Object`：所有类的超类
- #### hashCode 方法
  - 散列码`（hash code）` 是由对象导出的一个**整型值**。散列码是没有规律的。如果 x 和 y 是两个不同的对象， `x.hashCode( )` 与` y.hashCode( )` 基本上不会相同。
  - 由于`hashCode`方法定义在`Object`类中， 因此每个对象都有一个默认的散列码，其值为**对象的存储地址**。
  - 哈希码是一个32位的整数，它是由对象内部状态计算而得的，其目的是为了提高查找的效率。
  - 使用素数（如31）是为了帮助产生更好的散列分布。
 - 实例代码:
```
public class test {
    public static void main(String[] args) {
        String r="HELLO";
        StringBuilder rb=new StringBuilder(r);
        System.out.println(r.hashCode()+" "+rb.hashCode());
        String m=new String("HELLO");
        StringBuilder mb=new StringBuilder(m);
        System.out.println(m.hashCode()+" "+mb.hashCode());
    }
}
```
![](/Java/pic/java30.png)
- 其中字符串r与m有相同的散列码，这是由于字符串的散列码是由内容导出的。而字符串缓冲rb与mb却有不同的散列码， 这是因为在`StringBuffer`类中没有定义`hashCode`方法，它的散列码是由`Object`类的默认`hashCode`方法导出的对象存储地址。
- 需要组合多个散列值时，可以调用`Objects.hash`并提供多个参数。这个方法会对各个参数调用`Objects.hashCode`，并组合这些散列值。
- 可以简单写为：
```
public int hashCode{
   return Objects.hash(name, salary, hireDay);
}
```
- `Equals` 与 `hashCode` 的定义必须一致：如果 `x.equals(y)` 返回 `true`, 那么 `x.hashCode( )` 就必
须与 `y.hashCode( )` 具有相同的值。
- 注意：如果存在数组类型的域， 那么可以使用静态的 `Arrays.hashCode` 方法计算一个散列码，这个散列码由数组元素的散列码组成。
![](/Java/pic/java31.png)
- #### toString 方法
  - 设计子类的程序员应该定义自己的` toString` 方法，并将子类域的描述添加进去。如果超类使用了` getClass( ).getName( )`, 那么子类只要调用 `super.toString( )`就可以了。
- ### 泛型数组列表
  - `ArrayList` 是一个采用类型参数（type parameter） 的泛型类（ generic class）。
  - 声明和构造数组：
```
ArrayList<> staff = new ArrayList<>(); //也可添加初始容量
```
- 使用 `add` 方法可以将元素添加到数组列表中。
```
staff.add(new Employee("Harry Hacker", • • •));
staff.add(new Eraployee("Tony Tester", . . .));
```
- 如果已经清楚或能够估计出数组可能存储的元素数量， 就可以在填充数组之前调用`ensureCapacity`方法：
```
staff.ensureCapacity(数量)
```
- 分配数组列表和新数组分配空间：
```
new ArrayList<>(lOO) // capacity是返回字符串所占容器的总大小
new Employee[100] // size is 100 数组的大小
```
- **数组列表的容量与数组的大小**有一个非常重要的区别。如果为数组分配 100 个元素
的存储空间，数组就有 100 个空位置可以使用。 而容量为 100 个元素的数组列表只是拥
有保存 100 个元素的潜力 （ 实际上， 重新分配空间的话，将会超过100）, 但是在最初，
甚至完成初始化构造之后，数组列表根本就不含有任何元素。
- `size`方法将返回数组列表中**包含的实际元素数目**。例如，`staff.size`
将返回 `staff` 数组列表的**当前元素数量**， 它等价于数组 a 的`a.length`。
![](/Java/pic/java32.png)
![](/Java/pic/java33.png)
- ### 接口
  - 在 Java 程序设计语言中， 接口不是类，而是对类的一组需求描述，这些类要遵从接口描述的统一格式进行定义。
  - 定义接口的代码:**`public` `interface` 接口名** **//不要在定义接口的时候使用 `final` 关键字,也不可使用`private`,`protected`修饰符**
  - 若接口中有定义方法，那么在有类使用这个接口时，也要包含其方法。
  - 有类实现接口实例代码:**`public` `class` 类名 `implements` 接口名**
  - 接口的变量是隐式 `public static final`（常量），所以其值无法改变。
- #### 通过接口可以实现**多重继承**的目的
```
interface Happy{
    void Happy();
}
interface Pretty{
    void Pretty();
}
interface Extroverted{
    void Extroverted();
}

public class Girl implements Happy,Pretty,Extroverted{
    @Override
    public void Happy(){
        System.out.println("开心的女孩");
    }

    @Override
    public void Pretty() {
        System.out.println("漂亮的女孩");
    }

    @Override
    public void Extroverted() {
        System.out.println("外向的女孩");
    }
}
```
- 女孩类引用三个定义的接口并使用它们包含的方法，从而实现多重继承
- #### 实现多态
  - 多态可以通过继承（`extends`）的关系实现，也可以通过接口的形式实现。
  - 其实将父类对象应用于子类的特征就是多态。(将子类的对象看作为父类的实例化对象，即可调用父类的方法进而实现子类所需要)
  - `Override`(方法覆盖)与`Overload`(方法重载)之间的区别：重载`Overload`表示同一个类中可以有多个名称相同的方法，但这些方法的参数列表各不相同（即参数个数或类型不同），而`Override`不仅名称相同，参数列表也相同。
  - 实例代码:
```
public interface Shape { //Shape接口表示一个形状
    String name();
}
public class Circle implements Shape { //Circle 类实现了 Shape 接口，并重写了 name() 方法。
    @Override
    public String name() {
        return "圆";
    }
}
public class Square implements Shape { //Square 类也实现了 Shape 接口，并重写了 name() 方法。
    @Override
    public String name() {
        return "正方形";
    }
}
List<Shape> shapes = new ArrayList<>(); //测试类
Shape circleShape = new Circle();
Shape squareShape = new Square();

shapes.add(circleShape);
shapes.add(squareShape);

for (Shape shape : shapes) {
    System.out.println(shape.name());
}
```
```
public class test2 {
    interface Coach {
        void Command();
    }

    interface CoachFactory {
        Coach CreateCoach();
    }

    static class ACoach implements Coach {
        public void Command() {
            System.out.println("我是A级证书教练，其他都给我衮");
        }
    }

    static class ACoachFactory implements CoachFactory {
        public Coach CreateCoach() {
            return new ACoach();
        }
    }

    static class CCoach implements Coach {
        public void Command() {
            System.out.println("我是C级教练");
        }

        static class CCoachFactory implements CoachFactory {
            @Override
            public Coach CreateCoach() {
                return new CCoach();
            }
        }

        public class Demo {
            public static void create(CoachFactory factory) {
                factory.CreateCoach().Command();
            }

            public static void main(String[] args) {
                create(new ACoachFactory());
                create(new CCoachFactory());
            }
        }
    }
}
```
- ### 封装
  - 指利用抽象将数据和基于数据的操作封装在一起，使其构成一个不可分割的独立实体。 
  - 将对象的属性和行为封装起来，其载体就是类，类通常对客户隐藏其实现细节。
- 实例代码:
```
public class Husband {
   /*
     * 对属性的封装
     * 一个人的姓名、性别、年龄、妻子都是这个人的私有属性
     */
    private String name;
    private String sex;
    private int age;
    private Wife wife;
    /*
     * setter()、getter()是该对象对外开发的接口
     */
    public String getName(){
        return name;
    }
    public String setName(String name){
        this.name=name;
    }
    public String getSex(){
        return sex;
    }
    public String setSex(String sex){
        this.sex=sex;
    }

    public int getAge() {
        return age;
    }
    public int setAge(){
        this.age=age;
    }

    public void setWife(Wife wife) {
        this.wife=wife;
    }
}
```
- 封装确实可以使我们更容易地修改类的内部实现，而无需修改使用了该类的代码。
- 封装可以对成员变量进行更精确的控制。
- ### lambda 表达式
  - 一种 `lambda` 表达式形式：参数， 箭头（->） 以及一个表达式。如果代码要完成的计算无法放在一个表达式中，就可以像写方法一样，把这些代码放在 {}中，
并包含显式的 `return`语句
```
(String first, String second) -> //()内为参数
{ //需要完成的计算代码
if (first.length() < second.length())  
   return -1;
else if (first.length() > second.length()) 
   return 1;
else 
   return 0;
}
```
- 即使 lambda 表达式**没有参数**， 仍然要提供空括号，就像无参数方法一样：
```
() ->
{
  for(i=0,i<=100,i++)System.out.println(i); 
}
```
- ### 枚举类 
  - 枚举类型下的实例对象是其类所包含(拥有)的
  - 若你创建了Season这个类，那么其下就有春(SPRING),夏(SUMMER),秋(AUTUMN),冬(WINTER)，便要维护他们。
```
enum SeasonEnum{ //枚举季节类
    SPRING("春天"),SUMMER("夏天"),AUTUMN("秋天"),WINTER("冬天");

    private String chinese;
    SeasonEnum(String chinese){ //构造方法
        this.chinese=chinese; //调用this关键字
    }
    public String getchinese(){
        return chinese;
    }
}
public class Test {
    public static void main(String[] args) {
        String summer = "SUMMER";
        SeasonEnum season1 = SeasonEnum.SPRING;
        System.out.println(season1.getchinese());
    }
}
``` 
```
enum SeasonEnum{ //枚举季节类
    SPRING,SUMMER,AUTUMN,WINTER;
}
public class Test {
    public static void main(String[] args) {
        String summer="SUMMER";
        SeasonEnum season1=SeasonEnum.valueOf(summer); //使用valueOf，获取SUMMER的枚举类型
        SeasonEnum season2=SeasonEnum.SPRING; //直接初始化
        switch (season1){
            case SPRING:
                System.out.println("春天");
                break;
            case SUMMER:
                System.out.println("夏天");
                break;
            case AUTUMN:
                System.out.println("秋天");
                break;
            case WINTER:
                System.out.println("冬天");
                break;
        }
    }
}
```

- ### 集合类
![](/Java/pic/java35.png)
- #### Collection接口
  - `Collection`接口是层次结构中的根接口。构成`Collection`的单位称为元素。`Collection`接口通常不能直接使用，但该接口提供了添加元素、删除元素、管理数据的方法。由于`List`接口与`Set`接口都继承了`Collection`接口，因此这些方法对`List`集合与`Set`集合是通用的。
![](/Java/pic/java36.png)
```
public class p2 {
    public static void main(String[] args) {
        Collection <String>list=new ArrayList<>(); //实例化集合类对象
        list.add("地平线"); //向集合添加数据
        list.add("班加罗尔");
        list.add("直布罗陀");
        list.add("亡灵");
        Iterator<String> it=list.iterator(); //创建迭代器
        while (it.hasNext()){ //判断是否有下一个元素
            String apex=(String)it.next(); //获取集合中元素
            System.out.println(apex);
        }
    }
}
```
- #### List集合
  - `List`集合包括`List`接口以及`List`接口的所有实现类。`List`集合中的元素允许重复，各元素的顺序就是对象插入的顺序。类似Java数组，用户可通过使用索引（元素在集合中的位置）来访问集合中的元素。
  - `List`接口
    - List接口定义了两个重要方法
      - `get(int index)` ；获得指定索引位置。
      - `set(int index,Object obj)` ；将集合中指定索引位置的对象修改为指定对象。
    - List接口的常用实现类为`ArrayList`和`LinkedList`。
      - `ArrayList`类实现了可变的数组，允许保存所有元素，包括null，并可以根据索引位置对集合进行快速的随机访问；缺点是向指定的索引位置插入对象或删除对象的速度较慢。
      - `LinkedList`类采用**链表结构**保存对象。这种结构的优点是便于向集合中**插入和删除对象**，需要向集合中插入、删除对象时，使用`LinkedList`类实现的`List`集合的效率较高；但对于随机访问集合中的对象，使用`LinkedList`类实现`List`集合的效率较低。
      - 实例化对象时；`List<E> list=new ArrayList<>();`,其中E为数据类型，比如String。
- #### Set集合
  - `Set`集合中的对象不按特定的方式排序，只是简单地把对象加入集合中，但`Set`集合中不能包含重复对象。`Set`集合由`Set`接口和`Set`接口的实现类组成。`Set`接口继承了`Collection`接口，因此包含`Collection`接口的所有方法。
  - 其常用的实现类有`HashSet`类与`Treeset`类。
    - `HashSet`类实现`Set`接口，由哈希表（实际上是一个`HashMap`实例）支持。它不保证`Set`的迭代顺序，特别是它不保证该顺序恒久不变。此类允许使用`null`元素。 
    - `TreeSet`类不仅实现了`Set`接口，还实现了`java.util.SortedSet`接口，因此，`TreeSet`类实现的`Set`集合在遍历集合时按照自然顺序递增排序，也可以按照指定比较器递增排序，即可以通过比较器对用`TreeSet`类实现的`Set`集合中的对象进行排序。
![](/Java/pic/java37.png)
        - 存入`TreeSet`类实现的`Set`集合必须实现`Comparable`接口，该接口中的`compareTo(Object o)`方法比较此对象与指定对象的顺序。如果该对象小于、等于或大于指定对象，则分别返回负整数、0或正整数。
- #### Map集合
  - `Map`集合没有继承`Collection`接口，其提供的是`key`到`value`的映射。`Map`中不
能包含相同的`key`，每个`key`只能映射一个`value`。`key`还决定了存储对象在映射中的存储位置，但不是由`key`对象本身决定的，而是通过一种“散列技术”进行处理，产生一个散列码的整数值。散列码通常用作一个偏移量，该偏移量对应分配给映射的内存区域的起始位置，从而确定存储对象在映射中的存储位置。`Map`集合包括`Map`接口以及`Map`接口的所有实现类。
![](/Java/pic/java38.png)
```
public class p3 {
    public static void main(String[] args) {
        Map<String,String>map=new HashMap<>();
        map.put("01","atree");
        map.put("02","point");
        map.put("03","truth");
        map.put("04","coace");
        Set<String>set=map.keySet();
        Iterator<String>it= set.iterator();
        System.out.println("key集合中的所有元素:");
        while (it.hasNext()){
            System.out.println(it.next());
        }
        Collection<String>collection=map.values();
        it=collection.iterator();
        System.out.println("values集合中的元素：");
        while (it.hasNext()){
            System.out.println(it.next());
        }
    }
}
```
 - ##### Map接口的实现类
   - `Map`接口常用的实现类有`HashMap`和`TreeMap`。建议使用`HashMap`类实现`Map`集合，因为由`HashMap`类实现的`Map`集合添加和删除映射关系效率更高。`HashMap`是基于哈希表的`Map`接口的实现，`HashMap`通过哈希码对其内部的映射关系进行快速查找；而`TreeMap`中的映射关系存在一定的顺序，如果希望`Map`集合中的对象也存在一定的顺序，应该使用`TreeMap`类实现`Map`集合。 
   - `HashMap`类是基于哈希表的`Map`接口的实现，此实现提供所有可选的映射操作，并允许使用`null`值和`null`键，但必须保证键的唯一性。`HashMap`通过哈希表对其内部的映射关系进行快速查找。此类不保证映射的顺序，特别是它不保证该顺序恒久不变。
   - `TreeMap`类不仅实现了`Map`接口，还实现了`java.util.SortedMap`接口，因此，集合中的映射关系具有一定的顺序。但在添加、删除和定位映射关系时，`TreeMap`类比`HashMap`类性能稍差。由于`TreeMap`类实现的`Map`集合中的映射关系是根据键对象按照一定的顺序排列的，因此**不允许**键对象是`null`。
- ### I/O（输入／输出）
  - Java的I/O技术可以将数据保存到文本文件、二进制文件甚至是ZIP压缩文件中，以达到永久性保存数据的要求。
  - 流概述:流是一组有序的数据序列，根据操作的类型，可分为输入流和输出流两种。
I/O（`Input/Output`，输入／输出）流提供了一条通道程序，可以使用这条通道把
源中的字节序列送到目的地。虽然I/O流通常与磁盘文件存取有关，但是程序的源和
目的地也可以是键盘、鼠标、内存或显示器窗口等。
![](/Java/pic/java39.png) 
![](/Java/pic/java40.png)
- #### 输入／输出流
  - 其中，所有输入流类都是抽象类`InputStream`（字节输入流）或抽
象类`Reader`（字符输入流）的子类；而所有输出流都是抽象类`OutputStream`（字
节输出流）或抽象类`Writer`（字符输出流）的子类。
- **输入流**
  - `InputStream`类是字节输入流的抽象类，是所有字节输入流的父类。该类中所有方法遇到错误时都会引发`IOException`异常。
  - 包括的一些方法：
    - `read()`方法：从输入流中读取数据的下一个字节。返回0~255范围内的`int`字节值。如果因为已经到达流末尾而没有可用的字节，则返回值为-1。
    - `read(byte[] b)`：从输入流中读入一定长度的字节，并以整数的形式返回字节数。
    - `mark(int readlimit)`方法：在输入流的当前位置放置一个标记，`readlimit`参数告知此输入流在标记位置失效之前允许读取的字节数。
    - `reset()`方法：将输入指针返回到当前所做的标记处。
    - `skip(long n)`方法：跳过输入流上的n个字节并返回实际跳过的字节数。
    - `markSupported()`方法：如果当前流支持`mark()/reset()`操作就返回`true`。
    - `close`方法：关闭此输入流并释放与该流关联的所有系统资源。
![](/Java/pic/java41.png)
  - Java中的字符是`Unicode`编码，是双字节的。`InputStream`是用来处理字节的，并不适合处理字符文本。Java为字符文本的输入专门提供了一套单独的类`Reader`，但`Reader`类并不是`InputStream`类的替换者，只是在处理字符串时简化了编程。`Reader`类是字符输入流的抽象类，所有字符输入流的实现都是它的子类。
![](/Java/pic/java42.png)
- **输出流**
  - `OutputStream`类是字节输出流的抽象类，此抽象类是表示输出字节流的所有类的超类。
![](/Java/pic/java43.png)
  - `OutputStream`类中的所有方法均返回void，在遇到错误时会引发`IOException`异常。
  - 其中包括的一些方法：
    - `write(int b)`方法：将指定的字节写入此输出流。
    - `write(byte[] b)`方法：将b个字节从指定的`byte`数组写入此输出流。
    - `write(byte[] b,int off,int len)`方法：将指定`byte`数组中从偏移量`off`开始的`len`个字节写入此输出流。
    - `flush()`方法：彻底完成输出并清空缓存区。
    - `close()`方法：关闭输出流。
  - `Writer`类是字符输出流的抽象类，所有字符输出类的实现都是它的子类。
![](/Java/pic/java44.png)
- #### File类
  - `File`类是`java.io`包中唯一代表磁盘文件本身的对象。`File`类定义了一些与平台无关的方法来操作文件，可以通过调用`File`类中的方法，**实现创建、删除、重命名文件等操作**。`File`类的对象主要用来获取文件本身的一些信息，如文件所在的目录、文件的长度、文件读写权限等。数据流可以将数据写入到文件中，**文件**也是数据流最常用的**数据媒体**。
- ##### 文件的创建与删除
- 常用以下三种方法来构造函数：
  1. `File(String pathname)`
  语法如下：`new file(String pathname)`其中，`pathname`指路径名称（包含文件名）。例如：`File file = new File("d:/1.txt");`
  2. `File(String parent,String child)`
  该构造方法根据定义的父路径和子路径字符串（包含文件名）创建一个新的`File`对象。语法如下：`new File(String parent,String child)`
  3. `File(File f , String child)`该构造方法根据`parent`抽象路径名和`child`路径名字符串创建一个新`File`实例。语法如下：`new File(File f,String child)`
![](/Java/pic/java45.png)
```
public class p5 {
    public static void main(String[] args) {
        File file=new File("word.txt");
        if (file.exists()){
            file.delete();
            System.out.println("文件已删除");
        }else {
            try { //捕获可能出现的异常
                file.createNewFile(); //创建该文件
                System.out.println("文件已创建");
            } catch (Exception e){
                e.printStackTrace();
            }
        }
    }
}
```
```
public class p6 {
    public static void main(String[] args) {
        File file = new File("word.txt");
        if (file.exists()) {
            String filename=file.getName();
            long lenth=file.length();
            boolean hidden=file.isHidden();
            System.out.println("文件名称为："+filename);
            System.out.println("文件长度为："+lenth);
            System.out.println("文件是否为隐藏文件："+hidden);
        }else {
            System.out.println("文件不存在");
        }
    }
}
```
- #### 文件输入流\输出流
- ##### FileInputStream与FileOutputStream类
  - `FileInputStream`类与`FileOutputStream`类都用来操作磁盘文件。如果用户的文件读取需求比较简单，则可以使用`FileInputStream`类，该类继承自`InputStream`类。`FileOutputStream`类与`FileInputStream`类对应，提供了基本的文件写入能力。`FileOutputStream`类是`OutputStream`类的子类。 
```
public class p7 {
    public static void main(String[] args) {
        File file=new File("word.txt");
        try {
            FileOutputStream outputStream=new FileOutputStream(file);
            byte buy[]="玩APEX就应该享受，我也在享受，谁不在享受，享受就得应该享受，而不是不享受。".getBytes();
            outputStream.write(buy);
            outputStream.close();
        }catch (Exception e){
            e.printStackTrace();
        }
        try {
            FileInputStream inputStream=new FileInputStream(file);
            byte byt[]=new byte[1024]; //[]为数组大小，byte为字节数组
            int len=inputStream.read(byt);
            System.out.println("文件中的信息为："+new String(byt,0,len));
            inputStream.close();
        }catch (Exception e){
            e.printStackTrace();
        }
    }
}
```
  - `FileReader`和`FileWriter`类 
    - 使用`FileOutputStream`类向文件中写入数据与使用`FileInputStream`类从文件中将内容读出来，都存在一点不足，即这两个类都只提供了对字节或字节数组的读取方法。由于汉字在文件中占用两个字节，如果使用字节流，读取不好可能会出现乱码现象，此时采用字符流`Reader`或`Writer`类即可避免这种现象。`FileReader`和`FileWriter`字符流对应了`FileInputStream`和`FileOutputStream`类。`FileReader`流顺序地读取文件，只要不关闭流，每次调用`read()`方法就顺序地读取源中其余的内容，直到源的末尾或流被关闭。
- #### 带缓存的输入／输出流
  - 缓存是I/O的一种性能优化。缓存流为I/O流增加了内存缓存区。有了缓存区，使得在流上执行`skip()`、`mark()`和`reset()`方法都成为可能。   
  -  **`BufferedInputStream`与`BufferedOutputStream`类**
    - `BufferedInputStream`类可以对所有`InputStream`类进行带缓存区的包装以达到性能的优化。`BufferedInputStream`类有两个构造方法：
      - `BufferedInputStream(InputStream in)`。 
      - `BufferedInputStream(InputStream in,int size)`。
      - 第一种形式的构造方法**创建了一个带有32个字节的缓存流**；第二种形式的构造方法**按指定的大小来创建缓存区**。一个最优的缓存区的大小，取决于它所在的操作系统、可用的内存空间以及机器配置。从构造方法可以看出，`BufferedInputStream`对象位于`InputStream`类对象之前。
![](/Java/pic/java46.png)
  - **`BufferedReader`与`BufferedWriter`类**
    - 此两类分别继承`Reader`和`Writer`类。其具有内部缓存机制，可以以行为单位进行输入\输出。
![](/Java/pic/java47.png)
```
public class p6 {
    public static void main(String[] args) {
        String content[]={"Hi 好久不见","你过得还好吗？","我想你了","不是你不在我身边了,而感到寂寞","是因为我真的爱上你了","回来吧。"};
        File file=new File("word.txt");
        try {
            FileWriter fileWriter=new FileWriter(file);
            BufferedWriter buf=new BufferedWriter(fileWriter);
            for (int k = 0; k<content.length; k++){
                buf.write(content[k]);
                buf.newLine();
            }
            buf.close();
            fileWriter.close();
        }catch (Exception e){
            e.printStackTrace();
        }
        try {
            FileReader fileReader=new FileReader(file);
            BufferedReader bufr=new BufferedReader(fileReader);
            String s=null;
            int i=0;
            while ((s=bufr.readLine())!=null){
                i++;
                System.out.println("第"+i+"行："+s);
            }
        }catch (Exception e){
            e.printStackTrace();
        }
    }
}
```
  - #### 数据输入／输出流
    - 数据输入／输出流（`DataInputStream`类与`DataOutputStream`类）允许应用程序以与机器无关的方式从底层输入流中读取基本Java数据类型。也就是说，当读取一个数据时，不必再关心这个数值应当是哪种字节。
    - ![](/Java/pic/java48.png)
    - 由于Java中的字符是Unicode编码，是双字节的，`writeBytes`只是将字符串中的每一个字符的低字节内容写入目标设备中；而`writeChars`将字符串中的每一个字符的两个字节的内容都写到目标设备中；`writeUTF`将字符串按照`UTF`编码后的字节长度写入目标设备，然后才是每一个字节的`UTF`编码。
    - `DataInputStream`类只提供了一个`readUTF()`方法返回字符串。这是因为要在一个连续的字节流读取一个字符串，如果没有特殊的标记作为一个字符串的结尾，并且不知道这个字符串的长度，就无法知道读取到什么位置才是这个字符串的结束。
  - ####  ZIP压缩输入／输出流
    - `ZipOutputStream`与`ZipInputStream`类来实现文件的压缩／解压缩。无论是从ZIP压缩文件中读取内容还是写入内容进ZIP文件中都是先找到"目录进入点"。
    - ![](/Java/pic/java49.png)
    - ![](/Java/pic/java50.png)

- ### Java库中常见的集合类型：

|集合类型|描述|
|:----:|:----:|
|ArrayList|一种可以动态增长和缩减的索引序列|
|LinkedList|一种可以在任何位置进行高效地插人和删除操作的有序序列|
|ArrayDeque|一种用循环数组实现的双端队列|
|HashSet|一种没有重复元素的无序集合|
|TreeSet|一种有序集|
|EnumSet|一种包含枚举类型值的集|
|LinkedHashSet|一种可以记住元素插人次序的集|
|PriorityQueue|一种允许高效删除最小元素的集合|
|HashMap|一种存储键/值关联的数据结构|
|TreeMap|一种键值属于枚举类型的映射表|
|EnumMap|一种键值属于枚举类型的映射表|
|LinkedHashMap|一种可以记住键 / 值项添加次序的映射表|
|WeakHashMap|一种其值无用武之地后可以被垃圾回收器回收的映射表|
|IdentityHashMap|一种用==而不是equals()来比较键的映射表|
