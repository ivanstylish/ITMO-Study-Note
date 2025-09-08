package web;

import com.fastcgi.FCGIInterface;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

public class Main {

    // 存储历史结果
    private static final List<CheckResult> history = Collections.synchronizedList(new ArrayList<>());

    public static void main(String[] args) {
        FCGIInterface fcgi = new FCGIInterface();

        System.out.println("FastCGI Server started...");

        while (fcgi.FCGIaccept() >= 0) {
            long startTime = System.nanoTime();

            try {
                // 获取请求方法
                String requestMethod = System.getProperty("REQUEST_METHOD");
                String queryString = System.getProperty("QUERY_STRING");

                if ("GET".equals(requestMethod) && queryString != null) {
                    handleGetRequest(queryString, startTime);
                } else if ("POST".equals(requestMethod)) {
                    handlePostRequest();
                } else if ("OPTIONS".equals(requestMethod)) {
                    // 处理CORS预检请求
                    Response.sendCorsHeaders();
                } else {
                    Response.sendErrorResponse("Method not allowed");
                }

            } catch (Exception e) {
                Response.sendErrorResponse("Server error: " + e.getMessage());
                e.printStackTrace();
            }
        }
    }

    // 处理GET请求
    private static void handleGetRequest(String queryString, long startTime) {
        try {
            // 解析查询参数
            Map<String, String> params = Request.parseQueryString(queryString);

            // 获取参数
            double x = Request.getCoordinate(params, "x", 0);
            double y = Request.getCoordinate(params, "y", 0);
            double r = Request.getCoordinate(params, "r", 1);

            // 验证输入
            if (!CheckCoodi.valiableInput(x, y, r)) {
                Response.sendErrorResponse("Invalid input parameters");
                return;
            }

            // 检查点是否在区域内
            boolean isInArea = CheckCoodi.checkPoint(x, y, r);

            // 计算执行时间
            long endTime = System.nanoTime();
            double executionTime = (endTime - startTime) / 1_000_000.0; // 转换为毫秒

            // 创建结果对象
            CheckResult result = CheckResult.createWithCurrentTime(x, y, r, isInArea, executionTime);

            // 添加到历史记录
            history.add(result);

            // 检查是否请求HTML响应
            String accept = System.getProperty("HTTP_ACCEPT");
            if (accept != null && accept.contains("text/html")) {
                Response.sendHtmlResponse(result, history);
            } else {
                // 发送JSON响应
                Response.sendJsonResponse(result);
            }

        } catch (Exception e) {
            Response.sendErrorResponse("Request processing error: " + e.getMessage());
        }
    }

    // 处理POST请求
    private static void handlePostRequest() {
        try {
            String contentLength = System.getProperty("CONTENT_LENGTH");
            if (contentLength != null) {
                int len = Integer.parseInt(contentLength);
                byte[] input = new byte[len];
                System.in.read(input, 0, len);
                String body = new String(input, StandardCharsets.UTF_8);

                if (body.contains("action=clear")) {
                    history.clear();
                    Response.sendStatusResponse("cleared");
                } else if (body.contains("action=history")) {
                    // 返回历史记录
                    String historyJson = JsonUtil.listToJson(history);
                    Response.sendJsonResponse(historyJson);
                } else {
                    Response.sendErrorResponse("Unknown action");
                }
            }
        } catch (Exception e) {
            Response.sendErrorResponse("POST request processing error: " + e.getMessage());
        }
    }
}