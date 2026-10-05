package edu.lab.city;

import static org.assertj.core.api.Assertions.*;

import edu.lab.city.domain.*;

import jakarta.validation.*;

import org.junit.jupiter.api.Test;

class ValidationTest {
    // @Test：标记一个由 JUnit 执行的测试方法。
    @Test
    void rejectsBoundaryAndNonFiniteValuesAtOrmLevel() {
        try (var factory = Validation.buildDefaultValidatorFactory()) {
            var validator = factory.getValidator();
            var point = new Coordinates();
            point.setX(1L);
            point.setY(-531);
            assertThat(validator.validate(point)).isNotEmpty();
            point.setY(Double.NaN);
            assertThat(validator.validate(point)).isNotEmpty();
            point.setY(Double.POSITIVE_INFINITY);
            assertThat(validator.validate(point)).isNotEmpty();
            point.setY(-530.999);
            assertThat(validator.validate(point)).isEmpty();
            var human = new Human();
            human.setName(" ");
            human.setAge(0);
            human.setHeight(Float.POSITIVE_INFINITY);
            assertThat(validator.validate(human)).hasSizeGreaterThanOrEqualTo(3);
        }
    }

    @Test
    void birthdayConverterPreservesInstant() {
        var converter = new ZonedDateTimeConverter();
        var birthday = java.time.ZonedDateTime.parse("1990-01-02T03:04:05+03:00[Europe/Moscow]");
        assertThat(converter.convertToEntityAttribute(converter.convertToDatabaseColumn(birthday))
            .toInstant())
            .isEqualTo(birthday.toInstant());
        assertThat(converter.convertToEntityAttribute(null)).isNull();
    }
}
