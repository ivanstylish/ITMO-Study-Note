package server.commands;

import common.network.requests.Request;
import common.network.responses.*;
import server.repositories.ProductRepository;

/**
 * The 'info' command. Outputs information about the collection.
 */
public class Info extends Command {
  private final ProductRepository productRepository;

  public Info(ProductRepository productRepository) {
    super("info", "display collection information");
    this.productRepository = productRepository;
  }


  @Override
  public Response apply(Request request) {
    var lastInitTime = productRepository.getLastInitTime();
    var lastSaveTime = productRepository.getLastSaveTime();
    return new InfoResponse(productRepository.type(), String.valueOf(productRepository.size()), lastSaveTime, lastInitTime, null);
  }
}
