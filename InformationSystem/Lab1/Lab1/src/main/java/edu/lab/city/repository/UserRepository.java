package edu.lab.city.repository;

import edu.lab.city.domain.AppUser;

import jakarta.persistence.*;

import org.springframework.stereotype.Repository;

import java.util.Optional;

// @Repository：声明数据访问层 Spring Bean；此注解不代表使用了 Spring Data Repository。
@Repository
public class UserRepository {
    // @PersistenceContext：注入关联当前事务持久化上下文的 EntityManager 代理。
    @PersistenceContext
    private EntityManager em;

    public Optional<AppUser> findByUsername(String username) {
        return em.createQuery("select u from AppUser u where u.username = :name", AppUser.class)
            .setParameter("name", username)
            .getResultStream()
            .findFirst();
    }

    public void insert(AppUser user) {
        em.persist(user);
        em.flush();
    }
}
