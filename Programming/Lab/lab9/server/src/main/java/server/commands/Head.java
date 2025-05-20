package server.commands;

import common.network.requests.Request;
import common.network.responses.*;
import server.repositories.ProductRepository;

/**
 * The 'head' command. Outputs the first element of the collection.
 */
public class Head extends Command {
  private final ProductRepository productRepository;

  public Head(ProductRepository productRepository) {
    super("head", "output the first element of the collection");
    this.productRepository = productRepository;
  }

  @Override
  public Response apply(Request request) {
    try {
      return new HeadResponse(productRepository.first(), null);
    } catch (Exception e) {
      return new HeadResponse(null, e.toString());
    }
  }
}
