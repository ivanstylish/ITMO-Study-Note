package org.coordinate.bean;

import jakarta.annotation.PostConstruct;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.inject.Named;
import jakarta.persistence.*;

import org.coordinate.entity.Result;
import org.coordinate.mbean.JMXRegistration;

import java.io.Serializable;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

@Named("ResultBean")
@ApplicationScoped
public class ResultBean implements Serializable {

    public static final DateTimeFormatter FORMATTER =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    @PersistenceContext(unitName = "CoordinatePU")
    private EntityManager em;

    @Inject
    private JMXRegistration jmxRegistration;

    private List<ResultDTO> results = new ArrayList<>();

    @PostConstruct
    public void init() {
        loadResults();
    }

    private void loadResults() {
        List<Result> entities = em.createQuery(
                        "SELECT r FROM Result r ORDER BY r.checkTime DESC", Result.class)
                .getResultList();

        results = entities.stream()
                .map(ResultDTO::new)
                .toList();
    }

    public void addResult(double x, double y, double r, boolean hit) {
        long startTime = System.nanoTime();

        Result entity = new Result(x, y, r, hit, LocalDateTime.now(), 0L);
        em.persist(entity);
        em.flush();

        long executionTime = System.nanoTime() - startTime;
        entity.setExecutionTime(executionTime);
        // Update the persisted entity with actual execution time
        em.merge(entity);

        results.add(0, new ResultDTO(entity));

        // Record point statistics via MBean
        if (jmxRegistration != null && jmxRegistration.getPointsCounter() != null) {
            jmxRegistration.getPointsCounter().recordPoint(x, y, hit);
        }
    }

    public void clearResults() {
        em.createQuery("DELETE FROM Result").executeUpdate();
        em.createNativeQuery("ALTER SEQUENCE check_results_id_seq RESTART WITH 1")
                .executeUpdate();
        results.clear();
    }

    /**
     * Alias for clearResults() — used by JSF action binding.
     */
    public void clear() {
        clearResults();
    }

    public List<ResultDTO> getResults() {
        return results;
    }
}