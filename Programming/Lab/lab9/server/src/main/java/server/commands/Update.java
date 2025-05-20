package server.commands;

import common.exceptions.BadOwnerException;
import common.network.requests.*;
import common.network.responses.*;
import server.repositories.ProductRepository;

/**
 * The 'update' command. Updates an element of the collection.
 */
public class Update extends Command {
  private final ProductRepository productRepository;

  public Update(ProductRepository productRepository) {
    super("update <ID> {element}", "update the value of a collection item by ID");
    this.productRepository = productRepository;
  }

  @Override
  public Response apply(Request request) {
    var req = (UpdateRequest) request;
    try {
      if (!productRepository.checkExist(req.id)) {
        return new UpdateResponse("There is no product with this ID in the collection!");
      }
      if (!req.updatedProduct.validate()) {
        return new UpdateResponse( "Product fields are not valid! Product not updated!");
      }

      productRepository.update(req.getUser(), req.updatedProduct);
      return new UpdateResponse(null);
    } catch (BadOwnerException e) {
      return new UpdateResponse("BAD_OWNER");
    } catch (Exception e) {
      return new UpdateResponse(e.toString());
    }
  }
}
