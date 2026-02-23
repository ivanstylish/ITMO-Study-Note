package org.example;

public class MatrixPrinter {
    public static void printMatrix(double[][] matrix, String title) {
        System.out.println(title);
        for (double[] row : matrix) {
            for (double r : row) {
                System.out.print(r + " ");
            }
            System.out.println();
        }
        System.out.println();
    }

    public static void printArray(double[] x, String title) {
        System.out.println(title);
        for (int i = 0; i < x.length; i++) {
            System.out.printf("x%d = " + "%.4f" + "\n", i + 1, x[i]);
        }
        System.out.println();
    }
}
