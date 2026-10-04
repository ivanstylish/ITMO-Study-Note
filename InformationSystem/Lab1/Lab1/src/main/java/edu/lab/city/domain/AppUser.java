package edu.lab.city.domain;

import com.fasterxml.jackson.annotation.JsonIgnore;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "app_user")
public class AppUser {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    @Pattern(regexp = "[a-z0-9_]{3,32}")
    @Column(nullable = false, unique = true, length = 32)
    private String username;

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

    @PrePersist
    void initialize() {
        registeredAt = LocalDateTime.now(java.time.ZoneOffset.UTC);
    }
}
