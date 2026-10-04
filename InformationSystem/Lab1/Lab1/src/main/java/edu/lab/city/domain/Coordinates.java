package edu.lab.city.domain;

import com.fasterxml.jackson.annotation.JsonIgnore;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;

// @Entity：声明 JPA 实体；该类的对象可以映射到数据库记录。
@Entity
// @Table：指定实体对应的数据库表名。
@Table(name = "coordinates")
public class Coordinates {
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

    // @NotNull：校验值不能为 null；它不负责判断字符串是否为空或数字是否为正。
    @NotNull
    @Column(nullable = false)
    private Long x;

    // @DecimalMin：指定数值下界；inclusive=false 表示严格大于该值。
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

    // @AssertTrue：要求此校验方法返回 true，这里用于拒绝无穷大和 NaN。
    @AssertTrue(message = "y must be finite")
    // @JsonIgnore：不把此字段或属性输出到 JSON，避免暴露密码哈希或内部校验结果。
    @JsonIgnore
    public boolean isFiniteY() {
        return Double.isFinite(y);
    }
}
