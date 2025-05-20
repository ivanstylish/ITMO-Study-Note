package server.commands;

import common.model.Product;
import common.network.requests.*;
import common.network.responses.*;
import server.repositories.ProductRepository;

/**
 * The 'add_if_max' command. Adds a new item to the collection if its price is higher than the maximum price.
 */
public class AddIfMax extends Command {
  private final ProductRepository productRepository;

  public AddIfMax(ProductRepository productRepository) {
    super("add_if_max {element}", "add a new product to a collection if its price exceeds the maximum price of this collection");
    this.productRepository = productRepository;
  }

  @Override
  public Response apply(Request request) {
    try {
      var req = (AddIfMaxRequest) request;
      var maxPrice = maxPrice();
      if (req.product.getPrice() > maxPrice) {
        var newId = productRepository.add(req.getUser(), req.product);
        return new AddIfMaxResponse(true, newId, null);
      }
      return new AddIfMaxResponse(false, -1, null);
    } catch (Exception e) {
      return new AddIfMaxResponse(false, -1, e.toString());
    }
  }

  private Long maxPrice() {
    return productRepository.get().stream()
      .map(Product::getPrice)
      .mapToLong(Long::longValue)
      .max()
      .orElse(-1);
  }
}
