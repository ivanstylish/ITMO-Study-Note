package web;

import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;
import java.util.HashMap;
import java.util.Map;

class Request {

    // 解析查询字符串
    public static Map<String, String> parseQueryString(String query) throws UnsupportedEncodingException {
        Map<String, String> params = new HashMap<>();
        if (query != null && !query.isEmpty()) {
            String[] pairs = query.split("&");
            for (String pair : pairs) {
                String[] keyValue = pair.split("=");
                if (keyValue.length == 2) {
                    String key = URLDecoder.decode(keyValue[0], "UTF-8");
                    String value = URLDecoder.decode(keyValue[1], "UTF-8");
                    params.put(key, value);
                }
            }
        }
        return params;
    }

    // 从参数中提取坐标值
    public static double getCoordinate(Map<String, String> params, String key, double defaultValue) {
        try {
            return Double.parseDouble(params.getOrDefault(key, String.valueOf(defaultValue)));
        } catch (NumberFormatException e) {
            return defaultValue;
        }
    }
}
