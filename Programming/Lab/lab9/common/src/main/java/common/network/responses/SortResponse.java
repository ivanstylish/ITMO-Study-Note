package common.network.responses;

import common.model.Product;
import common.utility.Commands;

import java.util.List;

public class SortResponse extends Response{
  public final List<Product> products;

  public SortResponse(List<Product> products, String error) {
    super(Commands.SORT, error);
    this.products = products;
  }
}
