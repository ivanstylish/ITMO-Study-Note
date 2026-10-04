package edu.lab.city.domain;

import com.fasterxml.jackson.annotation.JsonIgnore;

import jakarta.persistence.*;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;

@Entity
@Table(name = "city")
public class City {
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

    @NotNull
    @Valid
    @ManyToOne(optional = false)
    @JoinColumn(name = "coordinates_id", nullable = false)
    private Coordinates coordinates;

    @NotNull
    @Column(name = "creation_date", nullable = false, updatable = false)
    private java.time.LocalDate creationDate;

    @Positive
    @Column(nullable = false)
    private float area;

    @Positive
    @Column(nullable = false)
    private long population;

    @Column(name = "establishment_date")
    private java.time.LocalDateTime establishmentDate;

    @Column(nullable = false)
    private boolean capital;

    @Column(name = "meters_above_sea_level")
    private Long metersAboveSeaLevel;

    @Enumerated(EnumType.STRING)
    private Climate climate;

    @Enumerated(EnumType.STRING)
    private Government government;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(name = "standard_of_living", nullable = false)
    private StandardOfLiving standardOfLiving;

    @Valid
    @ManyToOne
    @JoinColumn(name = "governor_id")
    private Human governor;

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

    public Coordinates getCoordinates() {
        return coordinates;
    }

    public void setCoordinates(Coordinates value) {
        this.coordinates = value;
    }

    public java.time.LocalDate getCreationDate() {
        return creationDate;
    }

    public void setCreationDate(java.time.LocalDate value) {
        this.creationDate = value;
    }

    public float getArea() {
        return area;
    }

    public void setArea(float value) {
        this.area = value;
    }

    public long getPopulation() {
        return population;
    }

    public void setPopulation(long value) {
        this.population = value;
    }

    public java.time.LocalDateTime getEstablishmentDate() {
        return establishmentDate;
    }

    public void setEstablishmentDate(java.time.LocalDateTime value) {
        this.establishmentDate = value;
    }

    public boolean getCapital() {
        return capital;
    }

    public void setCapital(boolean value) {
        this.capital = value;
    }

    public Long getMetersAboveSeaLevel() {
        return metersAboveSeaLevel;
    }

    public void setMetersAboveSeaLevel(Long value) {
        this.metersAboveSeaLevel = value;
    }

    public Climate getClimate() {
        return climate;
    }

    public void setClimate(Climate value) {
        this.climate = value;
    }

    public Government getGovernment() {
        return government;
    }

    public void setGovernment(Government value) {
        this.government = value;
    }

    public StandardOfLiving getStandardOfLiving() {
        return standardOfLiving;
    }

    public void setStandardOfLiving(StandardOfLiving value) {
        this.standardOfLiving = value;
    }

    public Human getGovernor() {
        return governor;
    }

    public void setGovernor(Human value) {
        this.governor = value;
    }

    @PrePersist
    void initialize() {
        creationDate = java.time.LocalDate.now(java.time.ZoneOffset.UTC);
    }

    @AssertTrue(message = "area must be finite")
    @JsonIgnore
    public boolean isFiniteArea() {
        return Float.isFinite(area);
    }
}
