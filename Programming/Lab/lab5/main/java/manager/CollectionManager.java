package manager;

import exception.InvalidInputException;
import model.Product;
import model.UnitOfMeasure;
import util.Console;
import util.FileUtils;
import util.JSONParser;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class CollectionManager {

    private final Stack<Product> collection = new Stack<>();
    private final String dataFile;
    private final Console console;

    public CollectionManager(String dataFile, Console console) {
        this.dataFile = dataFile;
        this.console = console;
        loadCollection();
    }

    private void loadCollection() {
        try {
            collection.addAll(JSONParser.parseCollection(FileUtils.readFile(dataFile)));
            IdGenerator.reset(collection);
            console.printSuccess("Loaded " + collection.size() + " items");
        } catch (Exception e) {
            console.printError("Load failed: " + e.getMessage());
        }
    }

    public void saveToFile() {
        try {
            String json = JSONParser.serializeCollection(collection);
            File file = new File(dataFile);
            try (FileOutputStream fos = new FileOutputStream(file)) {
                fos.write(json.getBytes(StandardCharsets.UTF_8)); // 显式指定编码
            }
            console.printSuccess("Data saved successfully");
        } catch (IOException e) {
            console.printError("Fail to save: " + e.getMessage());
        } catch (Exception e) {
            console.printError("Unexpected error: " + e.getMessage());
        }
    }

    public Optional<Product> findMinProduct() {
        return collection.stream().min(Product::compareTo);
    }

    public void addProduct(Product product) {
        collection.push(product);
        console.printSuccess("Product added successfully ID: " + product.getId());
    }

    public boolean removeProductByID(long id) {
        int initialSize = collection.size();
        collection.removeIf(p -> p.getId() == id);
        boolean success = collection.size() < initialSize; // 删除成功后的大小比初始小
        if (success) {
            console.printSuccess("Has been deleted with an ID of " + id + " product");
        }else {
            console.printError("Didn't find an ID of " + id + " product");
        }
        return success;
    }

    public void clearCollection() {
        collection.clear();
    }

    // 查询操作
    public Optional<Product> getProductById(long id) {
        return collection.stream()
                .filter(p -> p.getId() == id)
                .findFirst();
    }

    public void updateProduct(long id, Product newProduct) {
        boolean found = collection.stream().anyMatch(p -> p.getId() == id);

        if (found) {
            collection.replaceAll(p -> {
                if (p.getId() == id) {
                    newProduct.setId(id);
                    newProduct.setCreationDate(p.getCreationDate());
                    try {
                        newProduct.setCoordinates(p.getCoordinates());
                    } catch (InvalidInputException e) {
                        throw new RuntimeException(e);
                    }
                    try {
                        newProduct.setManufacturer(p.getManufacturer());
                    } catch (InvalidInputException e) {
                        throw new RuntimeException(e);
                    }
                    return newProduct;
                }
                return p;
            });
        }
    }

    public boolean insertProduct(int index, Product product) {
        if (index < 0 || index > collection.size()) {
            console.printError("Invalid index location: " + index);
            return false;
        }
        collection.add(index, product);
        console.printSuccess("Product inserted into position " + index);
        return true;
    }

    public void sortCollection() {
        Collections.sort(collection);
    }

    public boolean removeAnyByPrice(long price) {
        Optional<Product> product = collection.stream()
                .filter(product1 -> product1.getPrice() == price)
                .findFirst();

        return product.map(product1 -> {
            collection.remove(product1);
            console.printSuccess("Deleted the price " + price + " of product");
            return true;
        }).orElseGet(() -> {
            console.printInfo("Didn't find the price " + price + " of product");
            return false;
        });
    }

    public Optional<Product> getProductWithMaxDate() {
        return collection.stream()
                .max(Comparator.comparing(Product::getCreationDate));
    }

    public long CountByUnitOfMeasure(UnitOfMeasure unit) {
        return collection.stream()
                .filter(product -> product.getUnitOfMeasure() == unit)
                .count();
    }

    public Console getConsole() {
        return console;
    }

    public Stack<Product> getCollection() {
        return collection;
    }
}