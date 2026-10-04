package edu.lab.city.repository;

import edu.lab.city.domain.City;

import jakarta.persistence.*;

import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public class SpecialRepository {
    @PersistenceContext
    private EntityManager em;

    public Object average() {
        return em.createNativeQuery("select average_elevation()").getSingleResult();
    }

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
