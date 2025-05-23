package common.utility;

import common.model.Product;

import java.util.Comparator;

public class ProductComparator implements Comparator<Product> {
  public int compare(Product a, Product b){
    return a.getPrice().compareTo(b.getPrice());
  }
}
