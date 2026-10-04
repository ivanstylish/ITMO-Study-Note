package edu.lab.city.config;

import com.fasterxml.jackson.databind.ser.std.ToStringSerializer;

import org.springframework.boot.autoconfigure.jackson.Jackson2ObjectMapperBuilderCustomizer;
import org.springframework.context.annotation.*;

// @Configuration：声明 Spring 配置类，其中的 Bean 方法用于注册容器管理的对象。
@Configuration
public class JsonConfig {
    // 将 long 输出为字符串，防止浏览器丢失大整数精度；Jackson 仍可接收数字字符串。
    // @Bean：将方法返回的对象注册为 Spring Bean，供其他组件注入使用。
    @Bean
    Jackson2ObjectMapperBuilderCustomizer longAsString() {
        return builder -> builder
            .serializerByType(Long.class, ToStringSerializer.instance)
            .serializerByType(Long.TYPE, ToStringSerializer.instance);
    }
}
