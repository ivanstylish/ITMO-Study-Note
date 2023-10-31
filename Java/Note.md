## [主页](../README.md)/[Java](readme.md)/代码笔记
<head>
    <script src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML" type="text/javascript"></script>
    <script type="text/x-mathjax-config">
        MathJax.Hub.Config({
            tex2jax: {
            skipTags: ['script', 'noscript', 'style', 'textarea', 'pre'],
            inlineMath: [['$','$']]
            }
        });
    </script>
</head>

### Java主类结构
- Java程序的基本组成单元是类，类体中又包括属性与方法两部分
  - 通常将类的属性称为类的**全局变量**（成员变量），将方法中的属性称为**局部变量**。全局变量声明在类体中，局部变量声明在方法体中。全局变量和局部变量都有
各自的应用范围 
- 每一个应用程序都必须包含一个main()方法，含有main()方法的类称为主类
- 项目project、包package和类java class
- main()方法是类体中的主方法。该方法从“{”开始，至“}”结束。
public、static和void分别是main()方法的**权限修饰符、静态修饰符和返回值修饰符**，
Java程序中的main()方法必须声明为public static void。String[] args是一
个字符串类型的数组，它是main()方法的参数，main()方法是程序开始执行的位置。
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
  - 整数类型用来存储整数数值，即没有小数部分的数值。可以是正数，也可以是负数。整型数据在Java程序中有3种表示形式，分别为十进制、八进制和十六进制。
  - 整型数据根据它所占内存大小的不同，可分为byte、short、int和long 4种类型。
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
- 转义字符
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

