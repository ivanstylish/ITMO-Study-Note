package edu.lab.city.domain;

import com.fasterxml.jackson.annotation.JsonIgnore;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;

import java.time.LocalDateTime;

// @Entity：声明 JPA 实体；该类的对象可以映射到数据库记录。
@Entity
// @Table：指定实体对应的数据库表名。
@Table(name = "app_user")
public class AppUser {
    // @Id：标记主键字段，用来唯一识别一条记录。
    @Id
    // @GeneratedValue：IDENTITY 表示主键由数据库自增生成，新增时无需手动设置。
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // @NotBlank：校验字符串不能为 null、空串或只有空白字符。
    @NotBlank
    // @Pattern：使用正则表达式校验字符串格式，例如用户名允许的字符和长度。
    @Pattern(regexp = "[a-z0-9_]{3,32}")
    // @Column：配置字段对应的列；nullable、unique、updatable 等参数约束列映射。
    @Column(nullable = false, unique = true, length = 32)
    private String username;

    // @JsonIgnore：不把此字段或属性输出到 JSON，避免暴露密码哈希或内部校验结果。
    @JsonIgnore
    @NotBlank
    @Column(name = "password_hash", nullable = false, length = 60)
    private String passwordHash;

    @Column(name = "registered_at", nullable = false, updatable = false)
    private LocalDateTime registeredAt;

    public Long getId() {
        return id;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String value) {
        username = value;
    }

    public String getPasswordHash() {
        return passwordHash;
    }

    public void setPasswordHash(String value) {
        passwordHash = value;
    }

    // @PrePersist：JPA 首次保存对象前调用此方法，自动补充创建时间。
    @PrePersist
    void initialize() {
        registeredAt = LocalDateTime.now(java.time.ZoneOffset.UTC);
    }
}
