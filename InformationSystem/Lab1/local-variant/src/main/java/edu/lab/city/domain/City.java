package edu.lab.city.domain;

import com.fasterxml.jackson.annotation.JsonIgnore;

import jakarta.persistence.*;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;

// @Entity：声明 JPA 实体；该类的对象可以映射到数据库记录。
@Entity
// @Table：指定实体对应的数据库表名。
@Table(name = "city")
public class City {
    // @Id：标记主键字段，用来唯一识别一条记录。
    @Id
    // @GeneratedValue：IDENTITY 表示主键由数据库自增生成，新增时无需手动设置。
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    // @Positive：校验数值必须大于 0；若字段还要求非空，需要配合 NotNull。
    @Positive
    private Long id;

    // @Version：乐观锁版本号；提交时检查版本，防止旧数据覆盖他人的修改。
    @Version
    // @Column：配置字段对应的列；nullable、unique、updatable 等参数约束列映射。
    @Column(nullable = false)
    private Long version;

    // @NotBlank：校验字符串不能为 null、空串或只有空白字符。
    @NotBlank
    @Column(nullable = false, columnDefinition = "text")
    private String name;

    // @NotNull：校验值不能为 null；它不负责判断字符串是否为空或数字是否为正。
    @NotNull
    // @Valid：触发关联对象或请求 DTO 内部的校验约束，而不是只检查外层引用。
    @Valid
    // @ManyToOne：多对一关联：多个城市可引用同一个对象；optional=false 表示关联必填。
    @ManyToOne(optional = false)
    // @JoinColumn：指定保存关联对象主键的外键列。
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

    // @Enumerated：STRING 表示按枚举名称保存，避免枚举顺序变化影响已有数据。
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

    // @PrePersist：JPA 首次保存对象前调用此方法，自动补充创建时间。
    @PrePersist
    void initialize() {
        creationDate = java.time.LocalDate.now(java.time.ZoneOffset.UTC);
    }

    // @AssertTrue：要求此校验方法返回 true，这里用于拒绝无穷大和 NaN。
    @AssertTrue(message = "area must be finite")
    // @JsonIgnore：不把此字段或属性输出到 JSON，避免暴露密码哈希或内部校验结果。
    @JsonIgnore
    public boolean isFiniteArea() {
        return Float.isFinite(area);
    }
}
