package edu.lab.city.config;

import jakarta.persistence.EntityManagerFactory;

import org.springframework.context.annotation.*;
import org.springframework.orm.jpa.*;
import org.springframework.orm.jpa.vendor.EclipseLinkJpaVendorAdapter;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.annotation.EnableTransactionManagement;

import java.util.Map;

import javax.sql.DataSource;

@Configuration
@EnableTransactionManagement
public class PersistenceConfig {
    @Bean
    @DependsOn("flywayInitializer")
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
        return new JpaTransactionManager(factory);
    }
}
