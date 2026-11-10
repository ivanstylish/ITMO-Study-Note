package edu.lab.city;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

// @SpringBootApplication：Spring Boot 启动注解：启用自动配置，并扫描当前包及子包中的组件。
// @SpringBootApplication: аннотация для начальной загрузки Spring Boot; 
// включает автоконфигурацию и выполняет сканирование компонентов в текущем пакете и его подпакетах.
@SpringBootApplication
public class CityApplication {
    public static void main(String[] args) {
        SpringApplication.run(CityApplication.class, args);
    }
}
