package org.coordinate.bean;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.inject.Named;
import jakarta.persistence.EntityManager;
import jakarta.persistence.EntityManagerFactory;
import jakarta.persistence.Persistence;
import jakarta.persistence.TypedQuery;
import org.coordinate.entity.Result;
import org.coordinate.mbean.JMXRegistration;

import java.io.Serial;
import java.io.Serializable;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

@Named("ResultBean")
@ApplicationScoped
public class ResultBean implements Serializable {
    @Serial
    private static final long serialVersionUID = 1L;

    private static final Logger LOGGER = Logger.getLogger(ResultBean.class.getName());

    public static final DateTimeFormatter FORMATTER =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    @Inject
    private JMXRegistration jmxRegistration;

    private EntityManagerFactory emf;
    private List<ResultDTO> results;

    @PostConstruct
    public void init() {
        try {
            emf = Persistence.createEntityManagerFactory("CoordinatePU");
            loadResults();
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Failed to initialize EntityManagerFactory", e);
            results = new ArrayList<>();
        }
    }

    @PreDestroy
    public void destroy() {
        if (emf != null && emf.isOpen()) {
            emf.close();
        }
    }

    /**
     * Load all results from database
     */
    public void loadResults() {
        EntityManager em = null;
        try {
            em = emf.createEntityManager();
            TypedQuery<Result> query = em.createQuery(
                    "SELECT r FROM Result r ORDER BY r.checkTime DESC", Result.class);
            List<Result> entities = query.getResultList();

            results = new ArrayList<>();
            for (Result r : entities) {
                results.add(new ResultDTO(r));
            }
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Failed to load results", e);
            results = new ArrayList<>();
        } finally {
            if (em != null) {
                em.close();
            }
        }
    }

    /**
     * Add new check result with proper execution time measurement
     */
    public void addResult(double x, double y, double r, boolean hit) {
        long startTime = System.nanoTime();

        Result entity = new Result(x, y, r, hit, LocalDateTime.now(), 0L);

        EntityManager em = null;
        try {
            em = emf.createEntityManager();
            em.getTransaction().begin();
            em.persist(entity);
            em.getTransaction().commit();

            long executionTime = System.nanoTime() - startTime;
            entity.setExecutionTime(executionTime);

            // Update execution time in DB
            em.getTransaction().begin();
            em.merge(entity);
            em.getTransaction().commit();
        } catch (Exception e) {
            if (em != null && em.getTransaction().isActive()) {
                em.getTransaction().rollback();
            }
            LOGGER.log(Level.SEVERE, "Failed to persist result", e);
        } finally {
            if (em != null) {
                em.close();
            }
        }

        // Record point statistics via MBean
        if (jmxRegistration != null && jmxRegistration.getPointsCounter() != null) {
            jmxRegistration.getPointsCounter().recordPoint(x, y, hit);
        }

        loadResults();
    }

    /**
     * Clear all results — JSF action method
     */
    public void clear() {
        clearResults();
    }

    /**
     * Clear all results from database
     */
    private void clearResults() {
        EntityManager em = null;
        try {
            em = emf.createEntityManager();
            em.getTransaction().begin();
            em.createNativeQuery("TRUNCATE TABLE check_results RESTART IDENTITY").executeUpdate();
            em.getTransaction().commit();
        } catch (Exception e) {
            if (em != null && em.getTransaction().isActive()) {
                em.getTransaction().rollback();
            }
            LOGGER.log(Level.SEVERE, "Failed to clear results", e);
        } finally {
            if (em != null) {
                em.close();
            }
        }
        loadResults();
    }

    public List<ResultDTO> getResults() {
        if (results == null) {
            results = new ArrayList<>();
        }
        return results;
    }
}