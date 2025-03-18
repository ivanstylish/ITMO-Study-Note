package client.command;


import model.Product;

import java.io.Serial;

public class Add implements BaseCommand {
    @Serial
    private static final long serialVersionUID = 1L;
    private Product product;
    public Add(Product product) {
        this.product = product;
    }

    public Product getProduct() {
        return product;
    }

    public void setProduct(Product product) {
        this.product = product;
    }

    @Override
    public String getName() {
        return "add";
    }

    @Override
    public String getDescription() {
        return "добавить новый элемент в коллекцию";
    }
}
