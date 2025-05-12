package network;

import model.Product;

import java.util.List;

public interface UpdateListener {
    void onCollectionUpdate(List<Product> products);
}
