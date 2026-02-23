package org.example;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.InputMismatchException;
import java.util.Scanner;

public class Data {
    public static int dim;

    public static int getDim(){
        while (true) {
            System.out.println("Please enter the matrix dimension (0 <= n <= 20): \n>");
            try {
                Scanner s = new Scanner(System.in);
                dim = s.nextInt();
                if (dim < 0 || dim > 20) {
                    throw new InputMismatchException();
                }
                return dim;
            } catch (InputMismatchException e) {
                System.out.println("\033[31mPlease input a number from (0 <= n <= 20)!\033[0m");
            }
        }
    }

    public static double[][] matrixFromKeyboard (Scanner s){
        int dim = getDim();
        double[][] matrix = new double[dim][dim + 1];

        System.out.println("Please enter the extended matrix, each row " + (dim + 1) + " Count, separated by spaces, next line:");
        for (int i = 0; i < dim; i++) {
            System.out.print("Line " + (i + 1) + " : ");
            while (true) {
                try {
                    String line = s.nextLine().trim();
                    String[] tokens = line.split("\\s+");

                    if (tokens.length != dim + 1) {
                        System.out.println("\033[31mError: This line should have" + (dim + 1) + " count, please re-enter the value\033[0m");
                        continue;
                    }

                    for (int j = 0; j <= dim; j++) {
                        matrix[i][j] = Double.parseDouble(tokens[j]);
                    }
                    break;
                } catch (NumberFormatException e) {
                    System.out.println("\033[31mPlease enter a valid number! Please re-enter the line: \033[0m");
                }
            }
        }
        return matrix;
    }

    public static double[][] matrixFromFile() {
        Scanner s = new Scanner(System.in);
        final int MAX_ATTEMPTS = 5;
        int attempt = 0;

        while (attempt < MAX_ATTEMPTS) {
            attempt++;
            System.out.println("\nNum of ATTEMPTS: " + attempt + " / " + MAX_ATTEMPTS);
            System.out.println("""
                Please make sure that u got the right format of the matrix in the file like
                a    a    a    ...  a    b
                a    a    a    ...  a    b
                ...  ...  ...  ...  ...  ...
                Please enter the filename:
                >""");
            String filename = s.nextLine().trim();

            try (InputStream is = Data.class.getClassLoader().getResourceAsStream(filename)) {
                if (is == null) {
                    System.out.println("\033[31mThe file could not be found in the resources directory: " + filename + "\033[0m");
                    continue;
                }

                BufferedReader br = new BufferedReader(new InputStreamReader(is, StandardCharsets.UTF_8));

                br.mark(1000000);
                long lineCount = br.lines().filter(line -> !line.trim().isEmpty()).count();
                br.reset();

                if (lineCount < 1 || lineCount > 20) {
                    System.out.println("\033[0mInvalid num of lines (0 <= n <= 20)\033[0m");
                    continue;
                }

                int n = (int) lineCount;
                double[][] matrix = new double[n][n + 1];
                String line;
                int row = 0;

                while ((line = br.readLine()) != null) {
                    line = line.trim();
                    if (line.isEmpty()) continue;

                    String[] tokens = line.split("\\s+");
                    if (tokens.length != n + 1) {
                        System.out.println("\033[31mLine " + (row + 1) + " has wrong number of values (expected " + (n + 1) + ")\033[0m");
                        br.close();
                        continue;
                    }

                    for (int column = 0; column < tokens.length; column++) {
                        matrix[row][column] = Double.parseDouble(tokens[column]);
                    }
                    row++;
                }

                br.close();

                if (row != n) {
                    System.out.println("\033[31mFile reading incomplete\033[0m");
                    continue;
                }

                return matrix;
            } catch (FileNotFoundException e) {
                System.out.println("\033[31mFile not found, please re-enter the path!\033[0m");
            } catch (IOException | NumberFormatException e) {
                System.out.println("\033[31mError reading file: " + e.getMessage() + "\033[0m");
            }
        }
        System.out.println("\033[31mReach to MAX ATTEMPTS (" + MAX_ATTEMPTS + "), return to MENU.\033[0m");
        return null;
    }
 }
