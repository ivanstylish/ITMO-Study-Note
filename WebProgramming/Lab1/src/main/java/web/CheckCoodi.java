package web;

public class CheckCoodi {
    public static boolean valiableInput(double x, double y, double r) {
        double[] xAround = {-3, -2, -1, 0, 1, 2, 3, 4, 5};
        boolean xValid = false;
        for (double xa : xAround) {
            if (Math.abs(x - xa) < 0.01) {
                xValid = true;
                break;
            }
        }

        boolean yValid = y >= -5 && y <= 3;

        double[] rAround = {1, 2, 3, 4, 5};
        boolean rValid = false;
        for (double ra : rAround) {
            if (Math.abs(r - ra) < 0.01) {
                rValid = true;
                break;
            }
        }

        return xValid & yValid & rValid;
    }

    public static boolean checkPoint(double x, double y, double r) {
        // 第二象限：三角形
        if (x >= -r/2 && y <= r && (2 * x - y + r >= 0)) {
            return true;
        }
        // 第三象限：正方形
        if (x <=0 && x >= -r && y <= 0 && y >= -r) {
            return true;
        }
        // 第四象限：半弧
        if (x >= 0 && y <= 0) {
            return x * x + y * y <= (r / 2) * (r / 2);
        }
        return false;
    }
}
