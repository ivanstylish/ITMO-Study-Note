package org.example;

public class FormulaUtils {
    // 对角线优势
    public static boolean isDiagonal(double[][] m, int n) {
        for (int i = 0; i < n; i++) {
            double value = Math.abs(m[i][i]);
            double sum = 0.0;
            for (int j = 0; j < n; j++) {
                if (i != j) {
                    sum += Math.abs(m[i][j]);
                }
            }
            if (value <= sum) {
                return false;
            }
        }
        return true;
    }

    // 尝试重新排列线路，以实现严格的诊断优势
    public static boolean isReorderRows(double[][] m, int n) {
        // 记录哪些行被选为某个目标列的对角行
        boolean[] used = new boolean[n];

        // target为正在处理的行
        for (int target = 0; target < n; target++) {
            int bestRow = -1;
            double bValue = 0.0;

            for (int row = 0; row < n; row++) {
                if (used[row]) {
                    continue;
                }
                double value = Math.abs(m[row][target]);
                double oSum = 0.0;
                for (int j = 0; j < n; j++) {
                    if (j != target) {
                        oSum += Math.abs(m[row][j]);
                    }
                }
                if (value > oSum && value > bValue) {
                    bValue = value;
                    bestRow = row;
                }
            }
            if (bestRow == -1) {
                return false;
            }
            if (bestRow != target) {
                double[] temp = m[target];
                m[target] = m[bestRow];
                m[bestRow] = temp;
            }
            used[target] = true;
        }

        for (int i = 0; i < n; i++) {
            double value = Math.abs(m[i][i]);
            double sum = 0.0;
            for (int j = 0; j < n; j++) {
                if (i != j) {
                    sum += Math.abs(m[i][j]);
                }
                if (value <= sum) {
                    return false;
                }
            }
        }
        return true;
    }

    public static double iterMatNorm(double[][] m, int n) {
        double max = 0.0;
        for (int i = 0; i < n; i++) {
            double sum = 0.0;
            for (int j = 0; j < n; j++) {
                if (i != j) {
                    sum += Math.abs(m[i][j] / m[i][i]);
                }
            }
            max = Math.max(max, sum);
        }
        return max;
    }

    public static void printResidual(double[][] matrix, double[] x) {
        int n = matrix.length;
        System.out.println("\nCheck: residual vector r = b - A * x");
        System.out.println("-".repeat(50));

        double maxResidual = 0.0;
        for (int i = 0; i < n; i++) {
            double sum = 0.0;
            for (int j = 0; j < n; j++) {
                sum += matrix[i][j] * x[j];
            }
            double residual = Math.abs(matrix[i][n] - sum);
            maxResidual = Math.max(maxResidual, residual);
            System.out.printf("r%-2d = %.2e\n", i + 1, residual);
        }

        System.out.printf("\nMaximum discrepancy: %.2e\n", maxResidual);
        System.out.println("-".repeat(50));
    }
}
