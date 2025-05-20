package server.commands;

import common.model.Product;
import common.network.requests.Request;
import common.network.responses.*;
import server.repositories.ProductRepository;

/**
 * The 'sum_of_price' command. Sum of prices of all products.
 */
public class SumOfPrice extends Command {
  private final ProductRepository productRepository;

  public SumOfPrice(ProductRepository productRepository) {
    super("sum_of_price", "output the sum of price field values for all items in the collection");
    this.productRepository = productRepository;
  }

  @Override
  public Response apply(Request request) {
    try {
      return new SumOfPriceResponse(getSumOfPrice(), null);
    } catch (Exception e) {
      return new SumOfPriceResponse(-1, e.toString());
    }
  }

  private Long getSumOfPrice() {
    return productRepository.get().stream()
      .map(Product::getPrice)
      .mapToLong(Long::longValue)
      .sum();
  }
}
