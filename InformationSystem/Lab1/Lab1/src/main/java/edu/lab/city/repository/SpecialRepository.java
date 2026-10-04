package edu.lab.city.repository;

import edu.lab.city.domain.City;

import jakarta.persistence.*;

import org.springframework.stereotype.Repository;

import java.util.List;

// @Repository：声明数据访问层 Spring Bean；此注解不代表使用了 Spring Data Repository。
@Repository
public class SpecialRepository {
    // 五个特殊操作只调用 PostgreSQL 函数，计算规则仍保留在数据库层。
    // @PersistenceContext：注入关联当前事务持久化上下文的 EntityManager 代理。
    @PersistenceContext
    private EntityManager em;

    public Object average() {
        return em.createNativeQuery("select average_elevation()").getSingleResult();
    }

    // @SuppressWarnings：仅抑制指定编译警告；这里的 unchecked 来自原生查询结果的泛型转换。
    @SuppressWarnings("unchecked")
    public List<Object[]> groups() {
        return em.createNativeQuery("select * from group_by_area()").getResultList();
    }

    @SuppressWarnings("unchecked")
    public List<City> containing(String needle) {
        return em.createNativeQuery("select * from names_containing(?1)", City.class)
            .setParameter(1, needle)
            .getResultList();
    }

    public Object extremeRoute() {
        return em.createNativeQuery("select route_extreme_areas()").getSingleResult();
    }

    public Object newestRoute() {
        return em.createNativeQuery("select route_newest_city()").getSingleResult();
    }

    public String revision() {
        return em.createNativeQuery("select value from revision where id = 1")
            .getSingleResult()
            .toString();
    }
}
