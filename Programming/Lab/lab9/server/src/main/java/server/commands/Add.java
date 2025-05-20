package server.commands;

import common.network.requests.*;
import common.network.responses.*;
import server.repositories.ProductRepository;

/**
 * The 'add' command. Adds a new item to the collection.
 */
public class Add extends Command {
  private final ProductRepository productRepository;

  public Add(ProductRepository productRepository) {
    super("add {element}", "add a new product to the collection");
    this.productRepository = productRepository;
  }

  @Override
  public Response apply(Request request) {
    var req = (AddRequest) request;
    try {
      if (!req.product.validate()) {
        return new AddResponse(-1, "Product fields are not valid! Product not added!");
      }
      var newId = productRepository.add(req.getUser(), req.product);
      return new AddResponse(newId, null);
    } catch (Exception e) {
      return new AddResponse(-1, e.toString());
    }
  }
}
