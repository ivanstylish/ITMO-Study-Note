package common.model;

import common.user.User;
import common.utility.Element;

import java.io.Serial;
import java.time.LocalDate;
import java.util.Objects;

/**
 * Product class
 */
public class Product extends Element {
  @Serial
  private static final long serialVersionUID = 2L;

  private final int id; // Значение поля должно быть больше 0, Значение этого поля должно быть уникальным, Значение этого поля должно генерироваться автоматически
  private String name; // Поле не может быть null, Строка не может быть пустой
  private Coordinates coordinates; // Поле не может быть null
  private LocalDate creationDate; // Поле не может быть null, Значение этого поля должно генерироваться автоматически
  private Long price; // Поле не может быть null, Значение поля должно быть больше 0
  private UnitOfMeasure unitOfMeasure; // Поле может быть null
  private Organization manufacturer; // Поле может быть null

  private User creator;

  public Product(int id, String name, Coordinates coordinates, LocalDate creationDate,
                 Long price, UnitOfMeasure unitOfMeasure, Organization manufacturer, User creator) {
    this.id = id;
    this.name = name;
    this.coordinates = coordinates;
    this.creationDate = creationDate;
    this.price = price;
    this.unitOfMeasure = unitOfMeasure;
    this.manufacturer = manufacturer;
    this.creator = creator;
  }

  public Product copy(int id, User creator) {
    return new Product(id, this.name, this.coordinates, this.creationDate,
      this.price, this.unitOfMeasure, this.manufacturer, creator
    );
  }

  /**
   * Validates the correctness of the fields.
   * @return true, if true, otherwise false
   */
  @Override
  public boolean validate() {
    if (name == null || name.isEmpty())
      return false;
    if (coordinates == null)
      return false;
    if (creationDate == null)
      return false;
    if (price == null || price <= 0)
      return false;
    if (manufacturer != null) {
      return manufacturer.getName() != null && !manufacturer.getName().isEmpty() && manufacturer.getEmployeesCount() > 0;
    }
      return true;
  }

  public void update(Product product) {
    this.name = product.name;
    this.coordinates = product.coordinates;
    this.creationDate = product.creationDate;
    this.price = product.price;
    this.unitOfMeasure = product.unitOfMeasure;
    this.manufacturer = product.manufacturer;
  }

  @Override
  public int getId() {
    return id;
  }

  public String getName() {
    return name;
  }

  public Coordinates getCoordinates() {
    return coordinates;
  }

  public LocalDate getCreationDate() {
    return creationDate;
  }

  public Long getPrice() {
    return price;
  }


  public UnitOfMeasure getUnitOfMeasure() {
    return unitOfMeasure;
  }

  public Organization getManufacturer() {
    return manufacturer;
  }

  public int getCreatorId() {
    return creator.getId();
  }

  public User getCreator() {
    return creator;
  }

  public void setCreator(User creator) {
    this.creator = creator;
  }

  @Override
  public int compareTo(Element element) {
    return (this.id - element.getId());
  }

  public int compareTo(Product product) {
    return this.price.compareTo(product.price);
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) return true;
    if (o == null || getClass() != o.getClass()) return false;
    Product product = (Product) o;
    return id == product.id && Objects.equals(name, product.name) && Objects.equals(coordinates, product.coordinates)
      && Objects.equals(creationDate, product.creationDate) && Objects.equals(price, product.price)
      && unitOfMeasure == product.unitOfMeasure
      && Objects.equals(manufacturer, product.manufacturer);
  }

  @Override
  public int hashCode() {
    return Objects.hash(id, name, coordinates, creationDate, price, unitOfMeasure, manufacturer);
  }

  @Override
  public String toString() {
    String info = "";
    info += "Product №" + id;
    info += " (Added " + creationDate.toString() + ")";
    info += "\n Name: " + name;
    info += "\n Location: " + coordinates;
    info += "\n Price.: " + price;
    info += "\n Unit: " + unitOfMeasure;
    info += "\n Manufacturer:\n    " + manufacturer;
    info += "\n Creator: " + creator.toString();
    return info;
  }
}
