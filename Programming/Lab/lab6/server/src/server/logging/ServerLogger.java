package server.logging;

import java.io.IOException;
import java.util.logging.*;

public class ServerLogger {
    private static final Logger logger = Logger.getLogger(ServerLogger.class.getName());

    static {
        try {
            Handler fileHandler = new FileHandler("server.log", 10 * 1024 * 1024, 3, true);
            fileHandler.setFormatter(new SimpleFormatter());
            logger.addHandler(fileHandler);
            logger.setLevel(Level.ALL);
        } catch (IOException e) {
            logger.severe("Unable to initialize log file: " + e.getMessage());
            /* 错误处理 */}
    }

    // 记录服务器启动事件
    public static void logServerStart(int port) {
        logger.log(Level.INFO, "Server is up, listening on port: {0}", port);
    }

    // 记录命令执行
    public static void logCommand(String command) {
        logger.log(Level.INFO, "Execute command: {0}", command);
    }

    // 记录接收新请求
    public static void logNewRequest(String clientAddress) {
        logger.log(Level.INFO, "Received request from {0}", clientAddress);
    }

    // 记录错误事件
    public static void logError(String message, Throwable e) {
        logger.log(Level.SEVERE, message, e);
    }

    // 记录步骤信息
    public static void logInfo(String message) {
        logger.info(message);
    }

    /**
     * 自定义日志格式
     */
    private static class SimpleFormatter extends Formatter {
        @Override
        public String format(LogRecord record) {
            return String.format("[%1$tF %1$tT] [%2$-7s] %3$s %n",
                    record.getMillis(),
                    record.getLevel().getName(),
                    record.getMessage());
        }
    }
}
