package server.commands;

import common.exceptions.BadOwnerException;
import common.network.requests.*;
import common.network.responses.*;
import server.repositories.ProductRepository;

/**
 * The 'remove_by_id' command. Removes an item from the collection.
 */
public class RemoveById extends Command {
  private final ProductRepository productRepository;

  public RemoveById(ProductRepository productRepository) {
    super("remove_by_id <ID>", "remove a product from the collection by ID");
    this.productRepository = productRepository;
  }

  @Override
  public Response apply(Request request) {
    var req = (RemoveByIdRequest) request;

    try {
      if (!productRepository.checkExist(req.id)) {
        return new RemoveByIdResponse("There is no product with this ID in the collection!");
      }

      var removedCount = productRepository.remove(req.getUser(), req.id);
      if (removedCount <= 0) {
        return new RemoveByIdResponse("Nothing has been deleted!");
      }
      return new RemoveByIdResponse(null);
    } catch (BadOwnerException e) {
      return new RemoveByIdResponse("An attempt to remove someone else's product has been detected!");
    } catch (Exception e) {
      return new RemoveByIdResponse(e.toString());
    }
  }
}
