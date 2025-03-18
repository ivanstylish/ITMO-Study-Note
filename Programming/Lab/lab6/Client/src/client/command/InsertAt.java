package client.command;

import model.Product;

public class InsertAt implements BaseCommand {
    private int index;
    private Product product;
    public InsertAt(int index, Product product) {
        this.index = index;
        this.product = product;
    }

    public Product getProduct() {
        return product;
    }

    public int getIndex() {
        return index;
    }

    public void setIndex(int index) {
        this.index = index;
    }

    public void setProduct(Product product) {
        this.product = product;
    }

    @Override
    public String getName() {
        return "insert_at";
    }

    @Override
    public String getDescription() {
        return "добавить новый элемент в заданную позицию";
    }
}
