package logger;

import java.time.LocalDate;
import java.time.LocalDateTime;

public class Logger {
    public static void info(String message) {
        System.out.printf("[INFO] %s - %s\n", LocalDateTime.now(), message);
    }

    public static void error(String message) {
        System.out.printf("\u001B[31m[ERROR] %s - %s\n", LocalDateTime.now(), message + "\u001B[0m");
    }
}
