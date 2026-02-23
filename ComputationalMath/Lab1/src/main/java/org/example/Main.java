package org.example;

import java.util.InputMismatchException;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner s = new Scanner(System.in);
        System.out.println("Лабораторная работа 1. Метод простых итераций (вариант 15)\n");

        while (true) {
            System.out.println("1 - Input from keyboard");
            System.out.println("2 - Read from file");
            System.out.println("0 - EXIT");
            System.out.println("Please enter the num and choose ur mode!");

            int mode;
            try {
                mode = s.nextInt();
                s.nextLine();
            } catch (InputMismatchException e) {
                System.out.println("Input error. Enter the number 0, 1, or 2.");
                s.nextLine();
                continue;
            }

            double[][] matrix = new double[0][];

            if (mode == 1) {
                matrix = Data.matrixFromKeyboard(s);
            } else if (mode == 2) {
                System.out.print("Please give me the path of the file");
                matrix = Data.matrixFromFile();
            } else if (mode == 0) {
                System.out.println("""
                        Program gone away
                        * *
                         ^""");
                System.exit(0);
            } else {
                System.out.println("Invalid choice.\n" +
                        "Over.");
                return;
            }

            if (matrix.length == 0) {
                System.out.println("Data entry error.\n" +
                        "Over.");
                continue;
            }

            MatrixPrinter.printMatrix(matrix, "Original augmented matrix:");

            System.out.print("Accuracy: ");
            double eps = s.nextDouble();

            System.out.print("Maximum num of iterations: ");
            int maxIter = s.nextInt();

            SimpleIteration simple = new SimpleIteration(matrix, eps, maxIter);
            boolean success = simple.compute();

            if (success) {
                System.out.println("\n=== Final Result ===");
                System.out.println("Num of iterations: " + simple.getIterationCount());
                MatrixPrinter.printArray(simple.getSolution(), "Solution vector:");
                FormulaUtils.printResidual(matrix, simple.getSolution());
                System.out.println();
            } else {
                System.out.println("The solution could not be found with the specified accuracy.");
            }
        }
    }
}