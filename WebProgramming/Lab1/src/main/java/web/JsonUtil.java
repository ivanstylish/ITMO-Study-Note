package web;

import java.util.List;

class JsonUtil {


    // 将CheckResult列表转换为JSON数组
    public static String listToJson(List<CheckResult> list) {
        StringBuilder json = new StringBuilder("[");
        boolean first = true;

        for (CheckResult result : list) {
            if (!first) json.append(",");
            json.append(result.toJson());
            first = false;
        }

        json.append("]");
        return json.toString();
    }

    // 创建简单的状态JSON
    public static String createStatusJson(String status) {
        return String.format("{\"status\":\"%s\"}", status);
    }

    // 创建错误JSON
    public static String createErrorJson(String error) {
        return String.format("{\"error\":\"%s\"}", error);
    }
}