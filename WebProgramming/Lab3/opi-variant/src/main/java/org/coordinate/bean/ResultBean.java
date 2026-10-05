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

    @Inject
    private JMXRegistration jmxRegistration;
    
    private static final DateTimeFormatter FORMATTER =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private EntityManagerFactory emf;
    private List<ResultDTO> results;

    @PostConstruct
    public void init() {
        try {
            emf = Persistence.createEntityManagerFactory("CoordinatePU");
            loadResults();
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Failed to load results", e);
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
     * Add new check result with correct execution time measurement.
     * Timer wraps the actual database operations.
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
     * Clear all results - JSF action method
     */
    public String clear() {
        clearResults();
        return null;
    }

    /**
     * Clear all the results from database
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

    public void setResults(List<ResultDTO> results) {
        this.results = results;
    }

    /**
     * DTO class for displaying results in XHTML
     */
    public static class ResultDTO implements Serializable {
        private static final long serialVersionUID = 1L;
        private static final DateTimeFormatter FORMATTER =
                DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

        private Double x;
        private Double y;
        private Double r;
        private Boolean hit;
        private String timestamp;

        public ResultDTO(Result result) {
            this.x = result.getX();
            this.y = result.getY();
            this.r = result.getR();
            this.hit = result.getHit();
            this.timestamp = result.getCheckTime().format(FORMATTER);
        }

        public Double getX() {
            return x;
        }

        public Double getY() {
            return y;
        }

        public Double getR() {
            return r;
        }
        public Boolean getHit() {
            return hit;
        }
        public String getTimestamp() {
            return timestamp;
        }

        public void setX(Double x) {
            this.x = x;
        }
        public void setY(Double y) {
            this.y = y;
        }
        public void setR(Double r) {
            this.r = r;
        }
        public void setHit(Boolean hit) {
            this.hit = hit;
        }
        public void setTimestamp(String timestamp) {
            this.timestamp = timestamp;
        }
    }
}