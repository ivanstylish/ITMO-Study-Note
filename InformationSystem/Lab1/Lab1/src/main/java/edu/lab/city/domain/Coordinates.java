package edu.lab.city.domain;

import com.fasterxml.jackson.annotation.JsonIgnore;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;

@Entity
@Table(name = "coordinates")
public class Coordinates {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Positive
    private Long id;

    @Version
    @Column(nullable = false)
    private Long version;

    @NotNull
    @Column(nullable = false)
    private Long x;

    @DecimalMin(value = "-531", inclusive = false)
    @Column(nullable = false)
    private double y;

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

    public Long getX() {
        return x;
    }

    public void setX(Long value) {
        this.x = value;
    }

    public double getY() {
        return y;
    }

    public void setY(double value) {
        this.y = value;
    }

    @AssertTrue(message = "y must be finite")
    @JsonIgnore
    public boolean isFiniteY() {
        return Double.isFinite(y);
    }
}
