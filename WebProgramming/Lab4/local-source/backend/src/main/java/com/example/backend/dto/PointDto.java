package com.example.backend.dto;

import jakarta.validation.constraints.*;
import lombok.Getter;

@Getter
public class PointDto {
    @NotNull(message = "X coordinate is required")
    private Double x;

    @NotNull(message = "Y coordinate is required")
    private Double y;

    @NotNull(message = "R value is required")
    @DecimalMin(value = "0.01", message = "R must be positive (> 0)")
    @DecimalMax(value = "5.0", message = "R must be <= 5")
    private Double r;

    public void setX(Double x) {
        this.x = x;
    }

    public void setY(Double y) {
        this.y = y;
    }

    public void setR(Double r) {
        this.r = r;
    }
}