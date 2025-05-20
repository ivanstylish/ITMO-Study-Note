package server.commands;

import common.domain.Product;
import common.network.requests.*;
import common.network.responses.*;
import server.repositories.ProductRepository;

/**
 * The 'add_if_min' command. Adds a new item to the collection if its price is less than the minimum price.
 */
public class AddIfMin extends Command {
  private final ProductRepository productRepository;

  public AddIfMin(ProductRepository productRepository) {
    super("add_if_min {element}", "add a new product to a collection if its price is less than the minimum price of this collection");
    this.productRepository = productRepository;
  }


  @Override
  public Response apply(Request request) {
    try {
      var req = (AddIfMinRequest) request;
      var minPrice = minPrice();
      if (req.product.getPrice() < minPrice) {
        var newId = productRepository.add(req.getUser(), req.product);
        return new AddIfMinResponse(true, newId, null);
      }
      return new AddIfMinResponse(false, -1, null);
    } catch (Exception e) {
      return new AddIfMinResponse(false, -1, e.toString());
    }
  }

  private Long minPrice() {
    return productRepository.get().stream()
      .map(Product::getPrice)
      .mapToLong(Long::longValue)
      .min()
      .orElse(Long.MAX_VALUE);
  }
}
