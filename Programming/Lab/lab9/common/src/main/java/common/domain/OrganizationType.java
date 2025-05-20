package common.domain;

import java.io.Serializable;

/**
 * Enumeration of organisation types.
 */
public enum OrganizationType implements Serializable {
  COMMERCIAL,
  GOVERNMENT,
  TRUST,
  PRIVATE_LIMITED_COMPANY;

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
