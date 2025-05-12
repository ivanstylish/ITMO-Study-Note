package util;

import model.Product;

import java.util.List;

public class DataUpdateEvent {
    private final List<Product> products;

    public DataUpdateEvent(List<Product> products) {
        this.products = products;
    }

    public List<Product> getProducts() {
        return products;
    }
}
