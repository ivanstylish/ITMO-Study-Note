package edu.lab.city.domain;

import jakarta.persistence.AttributeConverter;
import jakarta.persistence.Converter;

import java.sql.Timestamp;
import java.time.*;

/** 保存同一时间点；从数据库读取时统一还原为 UTC 时区。 */
// @Converter：注册 JPA 类型转换器；autoApply=true 自动应用于匹配的 Java 字段类型。
@Converter(autoApply = true)
public class ZonedDateTimeConverter implements AttributeConverter<ZonedDateTime, Timestamp> {
    public Timestamp convertToDatabaseColumn(ZonedDateTime value) {
        return value == null ? null : Timestamp.from(value.toInstant());
    }

    public ZonedDateTime convertToEntityAttribute(Timestamp value) {
        return value == null ? null : value.toInstant().atZone(ZoneOffset.UTC);
    }
}
