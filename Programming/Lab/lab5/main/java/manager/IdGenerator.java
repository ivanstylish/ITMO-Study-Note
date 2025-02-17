package manager;

import model.Product;
import java.util.Stack;

public class IdGenerator {
    private static long productId = 1;
    private static int orgId = 1;
    private static long nextId = 1;
    public static synchronized long generateProductId() {
        return productId++;
    }

    public static synchronized int generateOrgId() {
        return orgId++;
    }

    public static void reset(Stack<Product> collection) {
        nextId = collection.stream()
                .mapToLong(Product::getId)
                .max()
                .orElse(0) + 1;
    }
}
