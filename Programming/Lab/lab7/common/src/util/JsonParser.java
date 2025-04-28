package util;


import model.Product;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class JsonParser {
    public static Product parseProduct(String json) {
        String name = extractStringValue(json, "name");
        long price = extractLongValue(json, "price");
        return new Product();
    }

    // 提取字符串字段值
    private static String extractStringValue(String json, String key) {
        Pattern pattern = Pattern.compile("\"" + key + "\":\"([^\"]+)\"");
        Matcher matcher = pattern.matcher(json);
        if (matcher.find()) {
            return matcher.group(1);
        }
        throw new IllegalArgumentException("Missing or invalid field: " + key);
    }

    // 提取长整型字段值
    private static long extractLongValue(String json, String key) {
        Pattern pattern = Pattern.compile("\"" + key + "\":(\\d+)");
        Matcher matcher = pattern.matcher(json);
        if (matcher.find()) {
            return Long.parseLong(matcher.group(1));
        }
        throw new IllegalArgumentException("Missing or invalid field: " + key);
    }
}
