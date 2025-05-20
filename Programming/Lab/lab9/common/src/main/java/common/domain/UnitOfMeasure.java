package common.domain;

import java.io.Serializable;

/**
 * A listing of the types of units of product measurement.
 */
public enum UnitOfMeasure implements Serializable {
  KILOGRAMS,
  SQUARE_METERS,
  LITERS,
  MILLILITERS;

  /**
   * @return A string with all enum elements through the string.
   */
  public static String names() {
    StringBuilder nameList = new StringBuilder();
    for (var weaponType : values()) {
      nameList.append(weaponType.name()).append(", ");
    }
    return nameList.substring(0, nameList.length()-2);
  }
}
