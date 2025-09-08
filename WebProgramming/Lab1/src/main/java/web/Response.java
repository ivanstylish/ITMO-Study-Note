package web;

import java.util.List;

class Response {

    // 发送JSON响应
    public static void sendJsonResponse(String json) {
        System.out.println("Content-Type: application/json");
        System.out.println("Access-Control-Allow-Origin: *");
        System.out.println("Access-Control-Allow-Methods: GET, POST, OPTIONS");
        System.out.println("Access-Control-Allow-Headers: Content-Type");
        System.out.println("Cache-Control: no-cache");
        System.out.println();
        System.out.println(json);
    }

    // 发送CheckResult的JSON响应
    public static void sendJsonResponse(CheckResult result) {
        sendJsonResponse(result.toJson());
    }

    // 发送错误响应
    public static void sendErrorResponse(String error) {
        sendJsonResponse(JsonUtil.createErrorJson(error));
    }

    // 发送状态响应
    public static void sendStatusResponse(String status) {
        sendJsonResponse(JsonUtil.createStatusJson(status));
    }

    // 发送CORS头
    public static void sendCorsHeaders() {
        System.out.println("Content-Type: text/plain");
        System.out.println("Access-Control-Allow-Origin: *");
        System.out.println("Access-Control-Allow-Methods: GET, POST, OPTIONS");
        System.out.println("Access-Control-Allow-Headers: Content-Type");
        System.out.println();
    }

    // 生成HTML响应
    public static void sendHtmlResponse(CheckResult result, List<CheckResult> history) {
        StringBuilder html = new StringBuilder();
        html.append("<!DOCTYPE html>\n");
        html.append("<html>\n");
        html.append("<head>\n");
        html.append("<meta charset=\"UTF-8\">\n");
        html.append("<title>Check result</title>\n");
        html.append("<style>\n");
        html.append("body { font-family: Arial, sans-serif; margin: 40px; }\n");
        html.append("table { border-collapse: collapse; width: 100%; }\n");
        html.append("th, td { border: 1px solid #ddd; padding: 12px; text-align: center; }\n");
        html.append("th { background-color: #4CAF50; color: white; }\n");
        html.append(".hit { background-color: #d4edda; }\n");
        html.append(".miss { background-color: #f8d7da; }\n");
        html.append("</style>\n");
        html.append("</head>\n");
        html.append("<body>\n");
        html.append("<h1>Point inspection results</h1>\n");
        html.append("<table>\n");
        html.append("<tr><th>Params</th><th>Value</th></tr>\n");
        html.append("<tr><td>X Coordinate</td><td>").append(result.getX()).append("</td></tr>\n");
        html.append("<tr><td>Y Coordinate</td><td>").append(result.getY()).append("</td></tr>\n");
        html.append("<tr><td>Radio R</td><td>").append(result.getR()).append("</td></tr>\n");
        html.append("<tr class=\"").append(result.isResult() ? "Hit" : "Miss").append("\">");
        html.append("<td>Result</td><td>").append(result.isResult() ? "Hit" : "Miss").append("</td></tr>\n");
        html.append("<tr><td>Current time</td><td>").append(result.getCurrentTime()).append("</td></tr>\n");
        html.append("<tr><td>Execution time</td><td>").append(String.format("%.3f ms", result.getExecutionTime())).append("</td></tr>\n");
        html.append("</table>\n");

        if (!history.isEmpty()) {
            html.append("<h2>History record</h2>\n");
            html.append("<table>\n");
            html.append("<tr><th>X</th><th>Y</th><th>R</th><th>Result</th><th>Time</th><th>Execution time(ms)</th></tr>\n");
            for (int i = history.size() - 1; i >= 0 && i >= history.size() - 10; i--) {
                CheckResult h = history.get(i);
                html.append("<tr class=\"").append(h.isResult() ? "Hit" : "Miss").append("\">");
                html.append("<td>").append(h.getX()).append("</td>");
                html.append("<td>").append(h.getY()).append("</td>");
                html.append("<td>").append(h.getR()).append("</td>");
                html.append("<td>").append(h.isResult() ? "Hit" : "Miss").append("</td>");
                html.append("<td>").append(h.getCurrentTime()).append("</td>");
                html.append("<td>").append(String.format("%.3f", h.getExecutionTime())).append("</td>");
                html.append("</tr>\n");
            }
            html.append("</table>\n");
        }

        html.append("</body>\n");
        html.append("</html>\n");

        System.out.println("Content-Type: text/html; charset=UTF-8");
        System.out.println("Access-Control-Allow-Origin: *");
        System.out.println();
        System.out.println(html);
    }
}