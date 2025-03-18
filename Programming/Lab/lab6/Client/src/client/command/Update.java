package client.command;

import model.Product;

public class Update implements BaseCommand {

    private final long id;
    private final Product product;

    public Update(long id, Product product) {
        this.id = id;
        this.product = product;
    }

    @Override
    public String getName() {
        return "update";
    }

    @Override
    public String getDescription() {
        return "обновить значение элемента коллекции, id которого равен заданному";
    }

    public Product getProduct() {
        return product;
    }
    public long getId() {
        return id;
    }
}
