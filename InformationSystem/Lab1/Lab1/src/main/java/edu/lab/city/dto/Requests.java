package edu.lab.city.dto;

import edu.lab.city.domain.*;

import jakarta.validation.constraints.*;

import java.time.*;

public final class Requests {
    private Requests() {}

    public record CityInput(
        @NotBlank String name,
        @NotNull @Positive Long coordinatesId,
        @NotNull @Positive Float area,
        @NotNull @Positive Long population,
        LocalDateTime establishmentDate,
        @NotNull Boolean capital,
        Long metersAboveSeaLevel,
        Climate climate,
        Government government,
        @NotNull StandardOfLiving standardOfLiving,
        @Positive Long governorId,
        @PositiveOrZero Long version) {}

    public record CoordinatesInput(
        @NotNull Long x,
        @NotNull @DecimalMin(value = "-531", inclusive = false) Double y,
        @PositiveOrZero Long version) {}

    public record HumanInput(
        @NotBlank String name,
        @NotNull @Positive Integer age,
        @NotNull @Positive Float height,
        ZonedDateTime birthday,
        @PositiveOrZero Long version) {}

    public record Page<T>(java.util.List<T> items, long total, int page, int size) {}

    public record Result(Object value, String explanation) {}
}
