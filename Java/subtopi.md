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
public abstract class Ivan {
    abstract void dad();
    Ivan(){
        System.out.println("before dad()");
        dad();
        System.out.println("after dad()");
    }

    public static void main(String[] args) {
        new son();
    }
}
class son extends Ivan{
    private int i=1;
    void dad(){
        System.out.println("dad()"+i);
    }
    public son(){
        System.out.println(i);
    }
}
```
9. 编写程序，实现读取文件时出现一个表示读取进度的进度条。可使用
javax.swing包提供的输入流类ProgressMonitorInputStream。
```
public class FileReadWithProgressBar {
    public static void main(String[] args) {
        // 选择文件
        JFileChooser fileChooser = new JFileChooser();
        int result = fileChooser.showOpenDialog(null);

        if (result == JFileChooser.APPROVE_OPTION) {
            // 获取选择的文件
            File selectedFile = fileChooser.getSelectedFile();

            // 设置进度条
            ProgressMonitor progressMonitor = new ProgressMonitor(null, "Reading File", "", 0, (int) selectedFile.length());
            try (FileInputStream fileInputStream = new FileInputStream(selectedFile);
                 BufferedInputStream bufferedInputStream = new BufferedInputStream(fileInputStream);
                 ProgressMonitorInputStream progressMonitorInputStream = new ProgressMonitorInputStream(null, "Reading File", bufferedInputStream)) {

                byte[] buffer = new byte[1024];
                int bytesRead;
                while ((bytesRead = progressMonitorInputStream.read(buffer)) != -1) {
                    // 处理文件数据，这里只是简单地模拟读取过程

                    // 更新进度条
                    progressMonitor.setProgress(progressMonitor.getMillisToPopup());
                }

                // 读取完成
                JOptionPane.showMessageDialog(null, "File Read Complete");

            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
```
10. 数字炸弹小游戏：输入玩家人数和名称，给定一个数字范围，玩家轮流猜数字，猜对了，炸弹爆炸，游戏结束。(Random，for循环，if和while条件语句，Scanner操作台来实现读取输入，hashmap集合记录玩家名称和分数，boolean逻辑语句)
```
public class NumberBombGame {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        //使用Scanner操作台来实现读取输入

        //输入数字范围
        System.out.println("Please enter a range of numbers：");
        int rangeStart = scanner.nextInt();
        int rangeEnd = scanner.nextInt();

        // 输入玩家的名称和数量
        System.out.println("Please enter the number of players：");
        int playNum = scanner.nextInt();
        scanner.nextLine(); //需在nextInt后加上nextLine才能正确换行

        //初始化玩家分数
        Map<String,Integer> playScores = new HashMap<>();
        for (int i = 1; i<=playNum; i++){
            System.out.println("Please enter the player's "+ i +" name:");
            String playerName = scanner.nextLine();
            playScores.put(playerName, 0);
        }

        //随机生成一个数字
        Random ran = new Random();
        int targetNMum = ran.nextInt(rangeEnd - rangeStart + 1) + rangeStart;

        //循环让每个玩家循环输入猜测的数字
        boolean isGameEnded = false;
        while (!isGameEnded){
            for (String playerName : playScores.keySet()) {
                System.out.println(playerName + " guess a number：");
                int guessNum = scanner.nextInt(); //玩家猜测的数字
                if (guessNum == targetNMum){ //如果猜对了，该玩家得分加10 ，游戏结束
                    playScores.put(playerName,playScores.get(playerName) + 10);
                    isGameEnded = true;
                    break;
                }else { //猜错，输出提示信息
                    String wrong = guessNum < targetNMum ?"It's smaller for it":"It's bigger for it";
                    System.out.println("You was tricked，" + wrong + "!");
                }
            }
        }

        //输出每个玩家的分数
        System.out.println("THE GAME IS OVER!");
        for (String playerName : playScores.keySet()){
            System.out.println(playerName + "points:" + playScores.get(playerName));
        }
    }
}
```
11. 编写程序，实现一个学生类，包含学生的姓名、年龄、性别、成绩、班级、入学时间等属性，并提供相应的构造方法和方法。
```
public class Student {
    private String name;
    private int age;
    private String gender;
    private double score;
    private String clazz;
    private Date enrollDate;

    public Student(String name, int age, String gender, double score, String clazz, Date enrollDate) {
        this.name = name;
        this.age = age;
        this.gender = gender;
        this.score = score;
        this.clazz = clazz;
        this.enrollDate = enrollDate;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getAge() {
        return age;
    }

    public void setAge(int age) {
        this.age = age;
    }

    public String getGender() {
        return gender;
    }

    public void setGender(String gender) {
        this.gender = gender;
    }

    public double getScore() {
        return score;
    }

    public void setScore(double score) {
        this.score = score;
    }

    public String getClazz() {
        return clazz;
    }

    public void setClazz(String clazz) {
        this.clazz = clazz;
    }

    public Date getEnrollDate() {
        return enrollDate;
    }

    public void setEnrollDate(Date enrollDate) {
        this.enrollDate = enrollDate;
    }

    public void printInfo() {
        System.out.println("Name:" + name);
        System.out.println("Age:" + age);
        System.out.println("Gender:" + gender);
        System.out.println("Score:" + score);
        System.out.println("Class:" + clazz);
        System.out.println("Enroll Date:" + enrollDate);
    }
}
```
12. 两数之和，给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出和为目标值 target 的那两个整数，并返回它们的数组下标。
```
public class Solution {
    public int[] twoSum(int[] nums, int target) {
        int n = nums.length;
        for (int i = 0; i < n; ++i) {
            for (int j = i + 1; j < n; ++j) {
                if (nums[i] + nums[j] == target) {
                    return new int[] {i,j};
                }
            }
        }
        return new int[0];
    }
}
// 或者用HashMap
 public class Solution {
    public int[] twoSum(int[] nums, int target) {
       Map<Integer, Integer> hashtable = new HashMap<Integer, Integer>();
       for(int i = 0; i < nums.length; ++i){
           if (hashtable.containsKey(target - nums[i])){
               return new int[]{hashtable.get(target - nums[i]), i};
           }
           hashtable.put(nums[i], i);
       }
       return new int[0];
    }
}
```
13. 给你一个 非严格递增排列 的数组 nums ，请你原地删除重复出现的元素，使每个元素 只出现一次 返回删除后数组的新长度。元素的 相对顺序 应该保持一致。然后返回 nums 中唯一元素的个数。
```
class Solution2 {
    public int removeDuplicates(int[] nums) {
        int slow = 0; //慢指针
        //快指针
        //找到不重复的元素，赋值到数组的开头
        for (int fast = 0; fast < nums.length; fast++){
            if (nums[fast] != nums[slow]) {
                nums[++slow] = nums[fast];
            }
        }
        return slow + 1;
    }
}
```