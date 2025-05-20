package server.commands;

import common.network.requests.Request;
import common.network.responses.Response;
import common.network.responses.SortResponse;
import server.repositories.ProductRepository;

public class Sort extends Command{
  private final ProductRepository productRepository;

  public Sort(ProductRepository productRepository) {
    super("Sort", "sort the collection in natural order");
    this.productRepository = productRepository;
  }
  @Override
  public Response apply(Request request) {
    try {
      var sortedProducts = productRepository.sorted();
      return new SortResponse(sortedProducts, null);
    } catch (Exception e) {
      return new SortResponse(null, e.toString());
    }
  }
}
