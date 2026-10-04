package edu.lab.city.domain;

import com.fasterxml.jackson.annotation.JsonIgnore;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;

@Entity
@Table(name = "human")
public class Human {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Positive
    private Long id;

    @Version
    @Column(nullable = false)
    private Long version;

    @NotBlank
    @Column(nullable = false, columnDefinition = "text")
    private String name;

    @Positive
    @Column(nullable = false)
    private int age;

    @Positive
    @Column(nullable = false)
    private float height;

    private java.time.ZonedDateTime birthday;

    public Long getId() {
        return id;
    }

    public void setId(Long value) {
        this.id = value;
    }

    public Long getVersion() {
        return version;
    }

    public void setVersion(Long value) {
        this.version = value;
    }

    public String getName() {
        return name;
    }

    public void setName(String value) {
        this.name = value;
    }

    public int getAge() {
        return age;
    }

    public void setAge(int value) {
        this.age = value;
    }

    public float getHeight() {
        return height;
    }

    public void setHeight(float value) {
        this.height = value;
    }

    public java.time.ZonedDateTime getBirthday() {
        return birthday;
    }

    public void setBirthday(java.time.ZonedDateTime value) {
        this.birthday = value;
    }

    @AssertTrue(message = "height must be finite")
    @JsonIgnore
    public boolean isFiniteHeight() {
        return Float.isFinite(height);
    }
}
