package common.network.responses;

import common.model.Product;
import common.utility.Commands;

public class MaxByCreationDateResponse extends Response{
  public final Product maxProduct;

  public MaxByCreationDateResponse(Product maxProduct, String error) {
    super(Commands.MAX_BY_CREATION_DATE, error);
    this.maxProduct = maxProduct;
  }
}
