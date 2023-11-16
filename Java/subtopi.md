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
