package com.example.backend.entity;

import jakarta.persistence.*;
import lombok.Getter;
import java.time.LocalDateTime;

@Getter
@Entity
@Table(name = "result")
public class Result {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private double x;
    private double y;
    private double r;
    private boolean hit;
    private LocalDateTime timestamp;

    public Result() {
    }

    public void setX(double x) {
        this.x = x;
    }

    public void setY(double y) {
        this.y = y;
    }

    public void setR(double r) {
        this.r = r;
    }

    public void setHit(boolean hit) {
        this.hit = hit;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }
}
