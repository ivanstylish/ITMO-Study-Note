package edu.lab.city.domain;

import com.fasterxml.jackson.annotation.JsonIgnore;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;

// @Entity：声明 JPA 实体；该类的对象可以映射到数据库记录。
@Entity
// @Table：指定实体对应的数据库表名。
@Table(name = "human")
public class Human {
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

    // @AssertTrue：要求此校验方法返回 true，这里用于拒绝无穷大和 NaN。
    @AssertTrue(message = "height must be finite")
    // @JsonIgnore：不把此字段或属性输出到 JSON，避免暴露密码哈希或内部校验结果。
    @JsonIgnore
    public boolean isFiniteHeight() {
        return Float.isFinite(height);
    }
}
