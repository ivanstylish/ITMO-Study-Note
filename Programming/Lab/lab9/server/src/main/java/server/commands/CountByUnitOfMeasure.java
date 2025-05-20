package server.commands;

import common.model.UnitOfMeasure;
import common.network.requests.CountByUnitOfMeasureRequest;
import common.network.requests.Request;
import common.network.responses.CountByUnitOfMeasureResponse;
import common.network.responses.Response;
import server.repositories.ProductRepository;

public class CountByUnitOfMeasure extends Command{
  private final ProductRepository productRepository;

  public CountByUnitOfMeasure(ProductRepository productRepository) {
    super("CountByUnitOfMeasure", "output the number of items whose unitOfMeasure field value is equal to the specified value");
    this.productRepository = productRepository;
  }

  @Override
  public Response apply(Request request) {
    var req = (CountByUnitOfMeasureRequest) request;
    try {
      UnitOfMeasure targetUnit = req.getUnit();
      long count = productRepository.get().stream()
        .filter(p -> p.getUnitOfMeasure() == targetUnit)
        .count();
      return new CountByUnitOfMeasureResponse(count, null);
    } catch (Exception e) {
      return new CountByUnitOfMeasureResponse(0, e.toString());
    }
  }
}
