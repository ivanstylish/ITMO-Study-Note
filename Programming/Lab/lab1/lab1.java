package lab1;

import java.util.Random;

public class lab1 {
    public static void main(String[] args) {
        ThreeArray twoArray = new ThreeArray(18, 16, -14.0f, 4.0f);
        twoArray.fillArray_z();
        twoArray.fillArray_x();
        twoArray.fillArray_z1();
        twoArray.print_result();
    }
}

class ThreeArray { // 创建新类，包含其属性，构造函数和方法
    short[] z;
    float[] x;
    double[][] z1;
    float max;
    float min;
    short num; // 用于填充 z 数组的起始值

    public ThreeArray(int num1, int num2, float min, float max) {
        z = new short[num1]; // 初始化数组
        x = new float[num2];
        z1 = new double[num1][num2];
        this.max = max;
        this.min = min;
        this.num = (short) (num1); // 初始化 num
    }

    void fillArray_z() {
        for (int i = 0; i < z.length; i++) {
            z[i] = num;
            num -= 1; // 从18开始降序
        }
    }

    void fillArray_x() {
        Random r = new Random();
        for (int j = 0; j < x.length; j++) {
            x[j] = min + r.nextFloat() * (max - min); // 修改为正确的随机数生成[min,max)
        }
    }

    void fillArray_z1() {
        for (int i = 0; i < z1.length; i++) {
            for (int j = 0; j < z1[i].length; j++) {
                if (z[i] == 15) {
                    z1[i][j] = Math.tan(Math.asin(Math.pow(Math.E, -Math.abs(x[j]))));
                } else if (z[i] == 2 || z[i] == 6 || z[i] == 7 || z[i] == 8 || z[i] == 9 || z[i] == 10 || z[i] == 11 || z[i] == 12 || z[i] == 14) {
                    z1[i][j] = Math.pow(Math.pow(x[j] / Math.PI, (Math.pow(x[j], 3) - 3) / 2) / Math.sin(Math.pow(x[j] * (x[j] + 1), x[j])) + 1, Math.pow(Math.atan((x[j] - 5) / 18) / 2, 3));
                } else {
                    z1[i][j] = Math.pow(((double) 1 / 2 + Math.pow((double) 1 / 3 * x[j], x[j])) / Math.log(Math.abs(x[j])) + 1, 2);
                }
            }
        }
    }

    void print_result() {
        for (double[] line : z1) { // 遍历二维数组z1的每一行
            for (double column : line) { // 遍历二维数组z1的每一列,是外层循环中每一行的 double 数组
                if (column < 0){
                    System.out.printf("-%.3f ", column); // 修改为正确的 printf 使用方式
                }else {
                    System.out.printf("+%.3f ", column); // 修改为正确的 printf 使用方式
                }
            }
            System.out.println();
        }
        System.out.println();
    }
}