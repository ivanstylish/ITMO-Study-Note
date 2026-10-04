package edu.lab.city.repository;

import edu.lab.city.domain.AppUser;

import jakarta.persistence.*;

import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public class UserRepository {
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
