package edu.lab.city.repository;

import edu.lab.city.domain.*;
import edu.lab.city.dto.Requests.Page;

import jakarta.persistence.*;

import org.springframework.stereotype.Repository;

import java.util.*;

// @Repository：声明数据访问层 Spring Bean；此注解不代表使用了 Spring Data Repository。
@Repository
public class ObjectRepository {
    // @PersistenceContext：注入关联当前事务持久化上下文的 EntityManager 代理。
    @PersistenceContext
    private EntityManager em;

    public <T> T find(Class<T> type, long id) {
        return em.find(type, id);
    }

    public <T> T insert(T object) {
        em.persist(object);
        em.flush();
        return object;
    }

    public void remove(Object object) {
        em.remove(object);
        em.flush();
    }

    public void flush() {
        em.flush();
    }

    public <T> List<T> all(Class<T> type) {
        return em.createQuery("select o from " + type.getSimpleName() + " o order by o.id", type)
            .getResultList();
    }

    public Page<City> cities(
        int page, int size, String column, String value, String sort, boolean desc) {
        // 只允许白名单列参与排序；用户提供的值通过参数绑定，不能拼入 SQL/JPQL。
        Map<String, String> fields = Map.of(
            "name", "c.name",
            "governorName", "h.name",
            "climate", "c.climate",
            "government", "c.government",
            "standardOfLiving", "c.standardOfLiving",
            "id", "c.id"
        );
        if (!fields.containsKey(sort)
            || (!column.isEmpty() && (!fields.containsKey(column) || column.equals("id")))) {
            throw new IllegalArgumentException("Unknown string column or sort field");
        }
        String from = " from City c left join c.governor h";
        Object parameter = value;
        String where = "";
        if (!column.isEmpty()) {
            try {
                parameter = switch (column) {
                    case "climate" -> Climate.valueOf(value);
                    case "government" -> Government.valueOf(value);
                    case "standardOfLiving" -> StandardOfLiving.valueOf(value);
                    default -> value;
                };
            } catch (IllegalArgumentException ex) {
                return new Page<>(List.of(), 0, page, size);
            }
            where = " where " + fields.get(column) + " = :value";
        }
        var count = em.createQuery("select count(c)" + from + where, Long.class);
        String orderBy = " order by " + fields.get(sort) + (desc ? " desc" : " asc")
            + (sort.equals("id") ? "" : ", c.id asc");
        var query = em.createQuery("select c" + from + where + orderBy, City.class);
        if (!where.isEmpty()) {
            count.setParameter("value", parameter);
            query.setParameter("value", parameter);
        }
        var items = query.setFirstResult(page * size).setMaxResults(size).getResultList();
        return new Page<>(items, count.getSingleResult(), page, size);
    }
}
