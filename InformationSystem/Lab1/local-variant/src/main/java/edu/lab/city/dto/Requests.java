package edu.lab.city.dto;

import edu.lab.city.domain.*;

import jakarta.validation.constraints.*;

import java.time.*;

public final class Requests {
    private Requests() {}

    public record CityInput(
        // @NotBlank：校验字符串不能为 null、空串或只有空白字符。
        @NotBlank String name,
        // @NotNull：校验值不能为 null；它不负责判断字符串是否为空或数字是否为正。
        // @Positive：校验数值必须大于 0；若字段还要求非空，需要配合 NotNull。
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
        // @PositiveOrZero：校验数值不能为负数，允许版本号从 0 开始；null 仍可表示未提供。
        @PositiveOrZero Long version) {}

    public record CoordinatesInput(
        @NotNull Long x,
        // @DecimalMin：指定数值下界；inclusive=false 表示严格大于该值。
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
