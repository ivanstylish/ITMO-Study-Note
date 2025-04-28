package model;

import exception.EmptyInputException;
import exception.InvalidInputException;

import java.io.Serializable;
import java.util.Date;

import static java.util.Objects.hash;

public class Product implements Comparable<Product>, Serializable {
    private Integer userId;
    private long id; //Значение поля должно быть больше 0, Значение этого поля должно быть уникальным, Значение этого поля должно генерироваться автоматически
    private String name; //Поле не может быть null, Строка не может быть пустой
    private Coordinates coordinates; //Поле не может быть null
    private java.util.Date creationDate; //Поле не может быть null, Значение этого поля должно генерироваться автоматически
    private long price; //Значение поля должно быть больше 0
    private UnitOfMeasure unitOfMeasure; //Поле может быть null
    private Organization manufacturer; //Поле не может быть null
    private int manufacturerId;


    public Product() {
        this.creationDate = new Date();
    }


    /**
     *关于产品和用户的一些字段获取方法
     */

    public Integer getUserId() {
        return userId;
    }

    public void setUserId(Integer userId) {
        this.userId = userId;
    }

    public long getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public Coordinates getCoordinates() {
        return coordinates;
    }

    public Date getCreationDate() {
        return creationDate;
    }

    public long getPrice() {
        return price;
    }

    public UnitOfMeasure getUnitOfMeasure() {
        return unitOfMeasure;
    }

    public Organization getManufacturer() {
        return manufacturer;
    }

    /**
     * go get setters
     */
    public void setName(String name) throws EmptyInputException {
        if (name == null || name.trim().isEmpty()) {
            throw new EmptyInputException("Name cannot be null or empty");
        }
        this.name = name.trim();
    }

    public void setCoordinates(Coordinates coordinates) throws InvalidInputException {
        if (coordinates == null) {
            throw new InvalidInputException("Coordinates cannot be null");
        }
        this.coordinates = coordinates;
    }

    public void setManufacturer(Organization manufacturer) throws InvalidInputException {
        if (manufacturer == null) {
            throw new InvalidInputException("Manufacturer cannot be null");
        }
        this.manufacturer = manufacturer;
    }

    public void setPrice(long price) throws InvalidInputException {
        if (this.price < 0) {
            throw new InvalidInputException("Price must be greater than 0");
        }
        this.price = price;
    }

    public void setUnitOfMeasure(UnitOfMeasure unitOfMeasure) {
        this.unitOfMeasure = unitOfMeasure;
    }


    public int compareTo(Product pro) {
        return Long.compare(this.price, pro.price);
    }

    @Override
    public String toString() {
        return String.format(
                "Product[id=%d, name='%s', price=%d, manufacturer='%s', creationDate=%s, coordinates=%s, unitOfMeasure='%s']",
                id, name, price, manufacturer, creationDate, coordinates, unitOfMeasure
        );
    }

    public void setId(long id) {
        this.id = id;
    }

    public void setCreationDate(Date creationDate) {
        this.creationDate = creationDate;
    }

    public int getManufacturerId() {
        return manufacturerId;
    }

    public void setManufacturerId(int manufacturerId) {
        this.manufacturerId = manufacturerId;
    }
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Product product = (Product) o;
        return id == product.id && price == product.price;
    }

    @Override
    public int hashCode() {
        return hash(id, price);
    }

}
