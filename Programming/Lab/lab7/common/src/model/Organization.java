package model;

import exception.InvalidInputException;

import java.io.Serializable;
import java.util.Objects;

public class Organization implements Serializable {
    private Integer id; //Поле не может быть null, Значение поля должно быть больше 0, Значение этого поля должно быть уникальным, Значение этого поля должно генерироваться автоматически
    private String name; //Поле не может быть null, Строка не может быть пустой
    private String fullName; //Значение этого поля должно быть уникальным, Длина строки не должна быть больше 1125, Поле не может быть null
    private OrganizationType type; //Поле не может быть null


    public Organization() {
    }
    public Integer getId() {
        return id;
    }
    public String getName() {
        return name;
    }
    public String getFullName() {
        return fullName;
    }
    public OrganizationType getType() {
        return type;
    }

    /**
     * set name when organization name = null or empty throws InvalidInputException
     * @param name
     */
    public void setName(String name) throws InvalidInputException {
        if (name == null || name.trim().isEmpty()) {
            throw new InvalidInputException("Organization name cannot be null or empty");
        }
        this.name = name;
    }

    /**
     * set fullname cannot be null and its length cannot be over than 1125
     * @param fullName
     * @throws InvalidInputException
     */
    public void setFullName(String fullName) throws InvalidInputException {
        if (fullName == null) {
            throw new InvalidInputException("Organization fullname cannot be null");
        } else if (fullName.length() > 1125) {
            throw new InvalidInputException("Organization Fullname length exceeds 1125 characters");
        }
        this.fullName = fullName;
    }

    /**
     * set type cannot be null
     * @param type
     * @throws InvalidInputException
     */
    public void setType(OrganizationType type) throws InvalidInputException {
        if (type == null) {
            throw new InvalidInputException("Organization type cannot be null");
        }
        this.type = type;
    }

    @Override
    public String toString() {
        return String.format(
                "Organization[id=%d, name='%s', type=%s]",
                id, name, type
        );
    }

    public void setId(int id) {
        this.id = id;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Organization that = (Organization) o;
        return Objects.equals(id, that.id) && Objects.equals(name, that.name) && type == that.type;
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, name, type);
    }


}

