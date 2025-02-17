package util;

import exception.InvalidInputException;
import model.*;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;

public class JSONParser {
    private static final SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssX");
    private static final String INDENT = "  "; // 缩进为 2 空格

    public static String serializeCollection(Stack<Product> collection) {
        StringBuilder json = new StringBuilder("[\n");
        for (Product p : collection) {
            String productJson = serializeProduct(p, 1); // 缩进级别为 1
            json.append(productJson).append(",\n");
        }
        if (!collection.isEmpty()) {
            json.delete(json.length() - 2, json.length()); // 删除最后一个逗号和换行
            json.append("\n");
        }
        json.append("]");
        return json.toString();
    }

    private static String serializeProduct(Product p, int indentLevel) {
        String indent = INDENT.repeat(indentLevel);
        String innerIndent = INDENT.repeat(indentLevel + 1);
        return String.format(
                "{\n" +
                        "%s\"id\":%d,\n" +
                        "%s\"name\":\"%s\",\n" +
                        "%s\"coordinates\":%s,\n" +
                        "%s\"price\":%d,\n" +
                        "%s\"organization\":%s,\n" +
                        "%s\"unitOfMeasure\":%s\n" +
                        "%s}",
                innerIndent, p.getId(),
                innerIndent, escapeJsonString(p.getName()),
                innerIndent, serializeCoordinates(p.getCoordinates()),
                innerIndent, p.getPrice(),
                innerIndent, serializeOrganization(p.getManufacturer(), indentLevel + 1),
                innerIndent, serializeUnitOfMeasure(p.getUnitOfMeasure()),
                indent
        );
    }

    private static String serializeCoordinates(Coordinates c) {
        return String.format(Locale.US, "{\"x\":%.2f,\"y\":%.2f}", c.getX(), c.getY());
    }

    private static String serializeUnitOfMeasure(UnitOfMeasure uom) {
        return (uom != null) ? "\"" + uom.name() + "\"" : "null";
    }

    private static String serializeOrganization(Organization o, int indentLevel) {
        String indent = INDENT.repeat(indentLevel);
        String innerIndent = INDENT.repeat(indentLevel + 1);
        return String.format(
                "{\n" +
                        "%s\"id\":%d,\n" +
                        "%s\"name\":\"%s\",\n" +
                        "%s\"fullName\":\"%s\",\n" +
                        "%s\"type\":\"%s\"\n" +
                        "%s}",
                innerIndent, o.getId(),
                innerIndent, escapeJsonString(o.getName()),
                innerIndent, escapeJsonString(o.getFullName()),
                innerIndent, o.getType().name(),
                indent
        );
    }

    private static String escapeJsonString(String str) {
        return str.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\b", "\\b")
                .replace("\f", "\\f")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t");
    }


    public static Stack<Product> parseCollection(String jsonData) {
        Stack<Product> products = new Stack<>();
        jsonData = jsonData.replaceAll("\\s+", "").replaceFirst("\\[", "").replaceFirst("\\]$", "");

        Arrays.stream(jsonData.split("(?<=}),"))
                .filter(s -> !s.isEmpty())
                .forEach(s -> {
                    try {
                        products.add(parseProduct(s));
                    } catch (InvalidInputException e) {
                        throw new RuntimeException(e);
                    }
                });

        return products;
    }

    private static Product parseProduct(String json) throws InvalidInputException {
        try {
            Map<String, String> fields = parseJsonObj(json);

            Product product = new Product();
            product.setId(Long.parseLong(fields.get("id")));
            product.setName(unescapeJsonString(fields.get("name")));
            product.setCoordinates(parseCoordinates(fields.get("coordinates")));
            product.setCreationDate(parseDate(fields.get("creationDate")));
            product.setPrice(Long.parseLong(fields.get("price")));
            product.setUnitOfMeasure(parseUnitOfMeasure(fields.get("unitOfMeasure")));
            product.setManufacturer(parseOrganization(fields.get("manufacturer")));

            return product;
        } catch (Exception e) {
            throw new InvalidInputException("Invalid product data: " + e.getMessage());
        }
    }

    private static Map<String, String> parseJsonObj(String json) {
        Map<String, String> map = new HashMap<>();
        json = json.trim().substring(1, json.length()-1);

        String[] pairs = json.split(",");
        for (String pair : pairs) {
            String[] keyValue = pair.split(":", 2);
            String key = keyValue[0].trim().replaceAll("\"", "");
            String value = keyValue[1].trim();

            if (value.startsWith("\"") && value.endsWith("\"")) {
                value = value.substring(1, value.length()-1);
            }
            map.put(key, value);
        }
        return map;
    }

    private static String unescapeJsonString(String str) {
        return str.replace("\\\"", "\"")
                .replace("\\\\", "\\")
                .replace("\\b", "\b")
                .replace("\\f", "\f")
                .replace("\\n", "\n")
                .replace("\\r", "\r")
                .replace("\\t", "\t");
    }

    private static Organization parseOrganization(String json) throws InvalidInputException {
        Map<String, String> fields = parseJsonObj(json);

        Organization org = new Organization();
        org.setId(Integer.parseInt(fields.get("id")));
        org.setName(unescapeJsonString(fields.get("name")));
        org.setFullName(unescapeJsonString(fields.get("fullname")));
        org.setType(OrganizationType.valueOf(fields.get("type")));

        return org;
    }

    private static UnitOfMeasure parseUnitOfMeasure(String unitOfMeasure) {
        if (unitOfMeasure == null || unitOfMeasure.equals("null")) {
            return null;
        }
        return UnitOfMeasure.valueOf(unitOfMeasure.replace("\"", ""));
    }

    private static Date parseDate(String creationDate) throws ParseException {
        return dateFormat.parse(creationDate);
    }

    private static Coordinates parseCoordinates(String json) throws InvalidInputException {
        Map<String, String> fields = parseJsonObj(json);
        double x = Double.parseDouble(fields.get("x"));
        float y = Float.parseFloat(fields.get("y"));
        return new Coordinates(x, y);
    }
}
