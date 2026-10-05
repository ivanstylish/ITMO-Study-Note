package edu.lab.city;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

// @SpringBootApplication：Spring Boot 启动注解：启用自动配置，并扫描当前包及子包中的组件。
@SpringBootApplication
public class CityApplication {
    public static void main(String[] args) {
        SpringApplication.run(CityApplication.class, args);
    }
}
