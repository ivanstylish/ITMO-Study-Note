package server.managers;


import exception.InvalidInputException;
import model.Product;
import model.UnitOfMeasure;
import server.file.FileUtils;
import server.file.JSONParser;
import server.logging.ServerLogger;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class CollectionManager {
    private Stack<Product> collection = new Stack<>();
    private final String filepath;

    public CollectionManager(String filepath) {
        this.filepath = filepath;
        loadCollection();
        initIdGenerator();
    }

    public void addProduct(Product product) {
        product.setId(IdGenerator.generateProductId());
        product.setCreationDate(new Date());
        collection.push(product);
        ServerLogger.logInfo("Successfully added a product ID: " + product.getId());
        saveCollection();
    }
    private void loadCollection() {
        try {
            collection.addAll(JSONParser.parseCollection(FileUtils.readFile(filepath)));
            IdGenerator.reset(collection);
            ServerLogger.logInfo("Loaded " + collection.size() + " products from file.");
        } catch (Exception e) {
            ServerLogger.logError("Failed to load collection: ", e);
            collection = new Stack<>();
        }
    }

    private void saveCollection() {
        try {
            String json = JSONParser.serializeCollection(collection);
            File file = new File(filepath);
            try (FileOutputStream fos = new FileOutputStream(file)) {
                fos.write(json.getBytes(StandardCharsets.UTF_8)); // 显式指定编码
            } catch (IOException e) {
                System.err.println("DEBUG: Save collection failed!");
                ServerLogger.logError("Failed to save collection: ", e);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        } catch (RuntimeException e) {
            throw new RuntimeException(e);
        }
    }

    public void removeProductByID(long id) {
        int initialSize = collection.size();
        collection.removeIf(p -> p.getId() == id);
        boolean success = collection.size() < initialSize;
        if (success) {
            ServerLogger.logInfo("Deleted product ID: " + id);
        } else {
            ServerLogger.logInfo("Product ID " + id + " not found.");
        }
    }

    public void clearCollection() {
        collection.clear();
        ServerLogger.logInfo("Collection cleared.");
    }

    public Optional<Product> getProduct() {
        // 假设我们要返回集合中的第一个产品
        return collection.stream()
                .findFirst();
    }


    public void updateProduct(long id, Product nProduct) {
        boolean found = collection.stream().anyMatch(p -> p.getId() == id);

        if (found) {
            collection.replaceAll(p -> {
                if (p.getId() == id) {
                    nProduct.setId(id);
                    nProduct.setCreationDate(p.getCreationDate());
                    try {
                        nProduct.setCoordinates(p.getCoordinates());
                    } catch (InvalidInputException e) {
                        throw new RuntimeException(e);
                    }
                    try {
                        nProduct.setManufacturer(p.getManufacturer());
                    } catch (InvalidInputException e) {
                        throw new RuntimeException(e);
                    }
                    return nProduct;
                }
                return p;
            });
        }
        ServerLogger.logInfo("Updated product successfully.");
    }

    public long countByUnitOfMeasure(UnitOfMeasure unit) {
        return collection.stream()
                .filter(p -> p.getUnitOfMeasure() == unit)
                .count();
    }

    public Stack<Product> getCollection() {
        return collection;
    }

    public boolean insertProduct(int index, Product product) {
        if (index < 0 || index > collection.size()) {
            return false;
        }
        collection.add(index, product);
        return true;
    }

    public void sortCollection() {
        Collections.sort(collection);
        ServerLogger.logInfo("Successfully sort collection!");
    }

    public void removeAnyByPrice(long price) {
        Optional<Product> product = collection.stream()
                .filter(product1 -> product1.getPrice() == price)
                .findFirst();

        product.map(product1 -> {
            collection.remove(product1);
            ServerLogger.logInfo("Deleted the price " + price + " of product");
            return true;
        }).orElseGet(() -> {
            ServerLogger.logInfo("Didn't find the price " + price + " of product");
            return false;
        });
    }

    public Optional<Product> getProductWithMaxDate() {
        return collection.stream()
                .max(Comparator.comparing(Product::getCreationDate));
    }
    private void initIdGenerator() {
        long maxProductId = collection.stream()
                .mapToLong(Product::getId)
                .max()
                .orElse(0);
        IdGenerator.setProductIdCounter(maxProductId + 1);

        int maxOrgId = collection.stream()
                .map(p -> p.getManufacturer().getId())
                .mapToInt(Integer::intValue)
                .max()
                .orElse(0);
        IdGenerator.setOrgIdCounter(maxOrgId + 1);
    }
}
