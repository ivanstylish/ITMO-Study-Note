package server.commands;

import common.model.Product;
import common.network.requests.Request;
import common.network.responses.MaxByCreationDateResponse;
import common.network.responses.Response;
import server.repositories.ProductRepository;

import java.util.Comparator;
import java.util.Optional;

public class MaxByCreationDate extends Command{
  private final ProductRepository productRepository;

  public MaxByCreationDate(ProductRepository productRepository) {
    super("MaxByCreationDate", "output any object from the collection whose creationDate field value is maximal");
    this.productRepository = productRepository;
  }

  @Override
  public Response apply(Request request) {
    try {
      // 获取创建时间最大的产品
      Optional<Product> maxProduct = productRepository.get().stream()
        .max(Comparator.comparing(Product::getCreationDate));
      return new MaxByCreationDateResponse(maxProduct.orElse(null), null);
    } catch (Exception e) {
      return new MaxByCreationDateResponse(null, e.toString());
    }
  }
}
