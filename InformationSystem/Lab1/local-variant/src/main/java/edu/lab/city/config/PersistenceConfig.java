package edu.lab.city.config;

import jakarta.persistence.EntityManagerFactory;

import org.springframework.context.annotation.*;
import org.springframework.orm.jpa.*;
import org.springframework.orm.jpa.vendor.EclipseLinkJpaVendorAdapter;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.annotation.EnableTransactionManagement;

import java.util.Map;

import javax.sql.DataSource;

// @Configuration：声明 Spring 配置类，其中的 Bean 方法用于注册容器管理的对象。
@Configuration
// @EnableTransactionManagement：启用声明式事务，让 Spring 代理处理 Transactional 方法。
// Включает декларативные транзакции, чтобы прокси-объекты Spring могли обрабатывать методы, помеченные аннотацией `@Transactional`.
@EnableTransactionManagement
public class PersistenceConfig {
    // @Bean：将方法返回的对象注册为 Spring Bean，供其他组件注入使用。
    // Зарегистрирует объект, возвращаемый методом, в качестве Spring-бина, чтобы его можно было внедрять в другие компоненты.
    @Bean
    // @DependsOn：指定初始化顺序：先执行 Flyway 数据库迁移，再创建持久化工厂。
    @DependsOn("flywayInitializer")
    // 先运行数据库迁移，再初始化 EclipseLink；不替换原项目的 ORM 实现。
    LocalContainerEntityManagerFactoryBean entityManagerFactory(DataSource dataSource) {
        var factory = new LocalContainerEntityManagerFactoryBean();
        factory.setDataSource(dataSource);
        factory.setPackagesToScan("edu.lab.city.domain");
        factory.setJpaVendorAdapter(new EclipseLinkJpaVendorAdapter());
        var properties = Map.of(
            "eclipselink.weaving", "false",
            "eclipselink.target-database", "org.eclipse.persistence.platform.database.PostgreSQLPlatform",
            "eclipselink.cache.shared.default", "false",
            "jakarta.persistence.validation.mode", "AUTO",
            "eclipselink.logging.level", "WARNING"
        );
        factory.setJpaPropertyMap(properties);
        return factory;
    }

    @Bean
    PlatformTransactionManager transactionManager(EntityManagerFactory factory) {
        // 服务层的 @Transactional 通过这里的事务管理器提交或回滚数据库修改。
        // Аннотация @Transactional в сервисном слое использует здесь менеджер транзакций для фиксации или отката изменений в базе данных.
        return new JpaTransactionManager(factory);
    }
}
