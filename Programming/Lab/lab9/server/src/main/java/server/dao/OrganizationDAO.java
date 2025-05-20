package server.dao;

import common.model.Organization;
import common.model.OrganizationType;
import jakarta.persistence.*;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import org.hibernate.annotations.Type;
import server.utils.OrganizationTypePostgreSql;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

@Entity(name="organizations")
@Table(name="organizations", uniqueConstraints={@UniqueConstraint(columnNames={"id"})})
public class OrganizationDAO implements Serializable {
  public OrganizationDAO() {
  }

  public OrganizationDAO(Organization organization) {
    this.name = organization.getName();
    this.employeesCount = organization.getEmployeesCount();
    this.type = organization.getType();
  }

  public void update(Organization organization) {
    this.name = organization.getName();
    this.employeesCount = organization.getEmployeesCount();
    this.type = organization.getType();
  }

  @Id
  @GeneratedValue(strategy=GenerationType.IDENTITY)
  @Column(name="id", nullable=false, unique=true, length=11)
  private int id;

  @NotBlank(message = "The name of the organisation should not be blank.")
  @Column(name="name", nullable=false)
  private String name; // Поле не может быть null, Строка не может быть пустой

  @Min(value = 1L, message = "The number of employees must be greater than zero.")
  @Column(name="employees_count", nullable=false)
  private long employeesCount; // Значение поля должно быть больше 0


  @Enumerated(EnumType.STRING)
  @Column(name = "type", nullable = false, columnDefinition = "organization_type")
  @Type(OrganizationTypePostgreSql.class)
  private OrganizationType type; // Поле не может быть null

  @OneToMany(cascade = CascadeType.REMOVE, fetch = FetchType.EAGER)
  @JoinColumn(name="manufacturer_id")
  private List<ProductDAO> products = new ArrayList<>();

  @ManyToOne
  @JoinColumn(name="creator_id", nullable=false)
  private UserDAO creator;

  public int getId() {
    return id;
  }

  public void setId(int id) {
    this.id = id;
  }

  public String getName() {
    return name;
  }

  public void setName(String name) {
    this.name = name;
  }

  public long getEmployeesCount() {
    return employeesCount;
  }

  public void setEmployeesCount(long employeesCount) {
    this.employeesCount = employeesCount;
  }

  public OrganizationType getType() {
    return type;
  }

  public void setType(OrganizationType type) {
    this.type = type;
  }

  public UserDAO getCreator() {
    return creator;
  }

  public void setCreator(UserDAO creator) {
    this.creator = creator;
  }

  public List<ProductDAO> getProducts() {
    return products;
  }

  public void setProducts(List<ProductDAO> products) {
    this.products = products;
  }
}
