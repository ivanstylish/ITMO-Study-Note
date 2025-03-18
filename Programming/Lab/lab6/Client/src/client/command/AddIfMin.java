package client.command;

import model.Product;

public class AddIfMin implements BaseCommand {
    private final Product product;

    public AddIfMin(Product product) {
        this.product = product;
    }

    @Override
    public String getName() {
        return "add_if_min";
    }

    @Override
    public String getDescription() {
        return "добавить новый элемент в коллекцию, если его значение меньше, чем у наименьшего элемента этой коллекции";
    }
}
