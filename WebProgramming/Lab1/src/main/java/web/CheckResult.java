package web;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

class CheckResult {
    private double x;
    private double y;
    private double r;
    private boolean result;
    private String currentTime;
    private double executionTime;

    public CheckResult(double x, double y, double r, boolean result, String currentTime, double executionTime) {
        this.x = x;
        this.y = y;
        this.r = r;
        this.result = result;
        this.currentTime = currentTime;
        this.executionTime = executionTime;
    }

    // Getters
    public double getX() {
        return x;
    }
    public double getY() {
        return y;
    }
    public double getR() {
        return r;
    }
    public boolean isResult() {
        return result;
    }
    public String getCurrentTime() {
        return currentTime;
    }
    public double getExecutionTime() {
        return executionTime;
    }

    // 转换为JSON字符串
    public String toJson() {
        return String.format(
                "{\"x\":%.2f,\"y\":%.2f,\"r\":%.2f,\"result\":%s,\"currentTime\":\"%s\",\"executionTime\":%.3f}",
                x, y, r, result ? "true" : "false", currentTime, executionTime
        );
    }

    // 静态方法：创建当前时间的结果
    public static CheckResult createWithCurrentTime(double x, double y, double r, boolean result, double executionTime) {
        String currentTime = LocalDateTime.now()
                .format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        return new CheckResult(x, y, r, result, currentTime, executionTime);
    }

    @Override
    public String toString() {
        return String.format("CheckResult(x=%.2f, y=%.2f, r=%.2f, result=%s, time=%s, execTime=%.3f ms)",
                x, y, r, result, currentTime, executionTime);
    }
}