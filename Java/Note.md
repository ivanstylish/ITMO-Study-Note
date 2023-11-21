## [主页](../README.md)/[Java](readme.md)/代码笔记

### Java主类结构
- Java程序的基本组成单元是类，类体中又包括属性与方法两部分
  - 通常将类的属性称为类的**全局变量**（成员变量），将方法中的属性称为**局部变量**。全局变量声明在类体中，局部变量声明在方法体中。全局变量和局部变量都有
各自的应用范围 
- 每一个应用程序都必须包含一个main()方法，含有main()方法的类称为主类
- 项目project、包package和类java class
- main()方法是类体中的主方法。该方法从“{”开始，至“}”结束。
public、static和void分别是main()方法的**权限修饰符、静态修饰符和返回值修饰符**，
Java程序中的main()方法必须声明为`public static void。String[] args`是一
个字符串类型的数组，它是`main()`方法的参数，main()方法是程序开始执行的位置。
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
double d2 =45678.1564;
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
 - 系统的内存可大略分为3个区域，即**系统（OS）区、程序
（Program）区和数据（Data）区**
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
### 三元运算符
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
- 为了了解成员变量，首先定义一个图书
类，成员变量对应于类对象的属性，在Book类中设置3个成员变量，分别为id、
name和category，分别对应于图书编号、图书名称和图书类别3个图书属性。
- 实例代码:
```

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
- **构造方法** 
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
- **构造方法**
  - `Boolean(boolean value)`
    - 该方法创建一个表示`value`参数的`Boolean`对象。
    - 例:`Boolean b = new Boolean(true);`
  - `Boolean(String str)`
    - 该方法以`String`变量作为参数创建`Boolean`对象。如果`String`参数不为`null`且在忽略大小写时等于true，则分配一个表示`true`值的Boolean对象，否则获得一个`false`值的Boolean对象。
    - 以String为变量，例:`Boolean bool = new Boolean("ok");`
![](/Java/pic/java21.png)