package org.example;

public class SimpleIteration {
    private final double[][] matrix;
    private final int n;
    private final int maxIterations;
    private final double eps;
    private double[] solution;
    private int iterationCount = 0;
    private boolean converged = false;

    public SimpleIteration(double[][] matrix, double eps, int maxIterations) {
        this.matrix = matrix;
        this.eps = eps;
        this.n = matrix.length;
        this.maxIterations = maxIterations;
        this.solution = new double[n];
    }

    boolean compute() {
        // 测试并尝试对角线优势
        if (!FormulaUtils.isDiagonal(matrix, n)) {
            System.out.println("No strict diagonal dominance -> row permutation");
            if (!FormulaUtils.isReorderRows(matrix, n)) {
                System.out.println("It is IMPOSSIBLE to achieve diagonal dominance!");
                return false;
            }
            System.out.println("Diagonal dominance achieved after permutation.");
            MatrixPrinter.printMatrix(matrix, "Matrix after permutation:");
        }

        // 迭代矩阵的范式
        double norms = FormulaUtils.iterMatNorm(matrix, n);
        System.out.printf("Iteration matrix norm: %.5f\n", norms);
        if (norms >= 1.0) {
            System.out.print("Attention: norm >= 1 -> convergence is not guaranteed!");
        }

        // 迭代
        double[] xOld = new double[n];
        double[] xNew = new double[n];

        System.out.println("\nIterations (errors by components):");

        while (iterationCount < maxIterations) {
            iterationCount++;

            for (int i = 0; i < n; i++) {
                double sum = matrix[i][n];
                for (int j = 0; j < n; j++) {
                    if (i != j) {
                        sum -= matrix[i][j] * xOld[j];
                    }
                }
                xNew[i] = sum / matrix[i][i];
            }

            // 误差
            double maxErr = 0.0;
            System.out.printf("IterationCount %3d |", iterationCount);
            for (int i = 0; i < n; i++) {
                double err = Math.abs(xNew[i] - xOld[i]);
                maxErr = Math.max(maxErr, err);
                System.out.printf("Change%d = %.2e ", i + 1, err);
            }
            System.out.println();

            System.arraycopy(xNew, 0, xOld, 0, n);

            if (maxErr < eps) {
                converged = true;
                break;
            }
        }

        solution = xOld.clone();
        return converged;
    }

    public double[] getSolution() {
        return solution;
    }

    public int getIterationCount() {
        return iterationCount;
    }
}
