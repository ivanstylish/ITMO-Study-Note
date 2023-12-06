## [主页](../README.md)/[Java](./readme.md)/测验小题

1. 逢7必过小游戏（从一到一百开始报数，所报数字含七或为七的倍数则输出“过”，否则输出该数字）
- 代码:
```
public class test1 {
    public static void main(String[] args) {
        for (int i=1;i<=100;i++){
            if (i%7==0){
                System.out.println("过");
            }else {
                System.out.println(i);
            }
        }
    }
}
```
2. 不调用MATH类进行算数平方根(只保留整数部分)
- 代码:
```
public class test2 {
    public static void main(String[] args) {
        int number=16;
        int x=(int)(Math.sqrt(number)); //强制转换
        System.out.println(x);
    }
}
```
3. 需求：定义一个数组，存入1~5。要求打乱数组中所有数据的顺序。
- 代码:
```
import java.util.Arrays;
import java.util.Random;

public class test5 {
    public static void main(String[] args) {
        int x[]={1,2,3,4,5}; //定义一个数组
        shuffleArray(x); //Array类shuffle的随机打乱
        System.out.println("打乱数组后为："+Arrays.toString(x)); //打印一维数组
    }

    public static void shuffleArray(int x[]) {
        Random random=new Random(); //随机数
        for (int i=x.length-1;i>0;i--){
            int j= random.nextInt(i+1); //生成一个1到i+1的随机数
            int temp=x[i]; //迭代位置的元素与随机位置的元素进行交换
            x[i]=x[j];
            x[j]=temp;
        }
    }
}
```
4. 给定一个数组及一个数字，判断这个数字是否在数组内。若在数组内返回true，若不在数组内返回false。
- 代码:
```
public class test6 {
    public static void main(String[] args) {
        int x[]={1,2,3,4,5,6,7,8}; //定义一个数组
        int number=4; //定义一个变量
        boolean b=b(x,number); //调用包含数字的方法(true用布尔)
        System.out.println("数组中是否含有该数字"+number+":"+b);
    }
    public static boolean b(int x[],int number){
        for (int y:x){ //使用for-each循环遍历数组
            if (y==number){ //若等于目标数字，则正确
                return true;
            }
        }
        return false;
    }
}
```
5.  尝试开发一个程序，获取2~32之间（不包括32）的6个偶数，并取得这6个偶数的和。
- 代码:
```
public class test14 {
    public static int x(int num1,int num2){
        int sum=0; //定义偶数和
        int count=0; //定义次数

        while (true){
            int y=(int)num1+(int)(Math.random()*(num2-num1));
            if (y!=0&&y%2==0){ //逻辑与(比较y是否等于0)
                System.out.println(y); //输出偶数
                sum+=y;
                count++;
            }
            if (count==6){
                break;
            }
        }
        return sum; //返回偶数之和
    }

    public static void main(String[] args) {
        System.out.println("任意2到32之间的6个偶数之和为:"+x(2,32)); //调用上面的方法
    }
}
```
6. 尝试开发一个程序，定义一个求圆面积的方法，其中以圆半径作为参数，并将计算结果保留5位小数。
- 代码:
```
import java.text.DecimalFormat;

public class test15 {
    static public void SimpleFormat(String pattern,double value){
        DecimalFormat myFormat=new DecimalFormat();
        String put= myFormat.format(value);
        System.out.println("圆的面积："+value+""+put);
    }
    public static double GetAroundArea(double r){
        return Math.PI*Math.pow(r,2);
    }

    public static void main(String[] args) {
        System.out.println();
        SimpleFormat("圆的面积保留五位小数:"+"#.#####",GetAroundArea(2));
    }
}
```
7. 尝试创建一个父类，在父类中创建两个方法，在子类中覆盖第二个方法，再
为子类创建一个对象，将它向上转型到基类并调用这个方法。
```
public class bird {
    public void cuckoo() {
        System.out.println("杜鹃"); //父类创建的第一个方法
    }

    public void owl() {
        System.out.println("猫头鹰"); //父类创建的第二个方法
    }

    public static void main(String[] args) {
        bird u = new sub(); //向上转型，将父类对象实例化
        u.cuckoo(); //使用u对象成员方法
        u.owl(); //使用u对象成员方法
    }
}
class sub extends bird{ //将上一类继承父类
    public void owl(){
            System.out.println("被修改后的猫头鹰"); //子类修改父类的方法二
    }
}
```
8. 尝试创建一个父类和子类，分别创建构造方法，然后向父类和子类添加成员
变量和方法，并总结构建子类对象时的顺序。
```
public class bird {
    public void cuckoo() {
        System.out.println("杜鹃"); //父类创建的第一个方法
    }

    public void owl() {
        System.out.println("猫头鹰"); //父类创建的第二个方法
    }

    public static void main(String[] args) {
        bird u = new sub(); //向上转型，将父类对象实例化
        u.cuckoo(); //使用u对象成员方法
        u.owl(); //使用u对象成员方法
    }
}
class sub extends bird{ //将上一类继承父类
    public void owl(){
            System.out.println("被修改后的猫头鹰"); //子类修改父类的方法二
    }
}
```