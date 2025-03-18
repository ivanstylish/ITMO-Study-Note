package server.managers;

import model.Product;
import java.util.Stack;

public class IdGenerator {
    private static long productId = 1;
    private static int orgId = 1;
    public static synchronized long generateProductId() {
        return productId++;
    }

    public static synchronized int generateOrgId() {
        return orgId++;
    }

    public static synchronized void reset(Stack<Product> collection) {
        productId = collection.stream()
                .mapToLong(Product::getId)
                .max()
                .orElse(0) + 1;
    }

    public static void setProductIdCounter(long start) {
        productId = start;
    }

    public static void setOrgIdCounter(int start) {
        orgId = start;
    }
}
