package org.coordinate.mbean;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Named;

import javax.management.MBeanServer;
import javax.management.ObjectName;
import java.lang.management.ManagementFactory;
import java.util.logging.Level;
import java.util.logging.Logger;


@Named("JMXRegistration")
@ApplicationScoped
public class JMXRegistration {

    private static final Logger LOGGER = Logger.getLogger(JMXRegistration.class.getName());

    private static final String DOMAIN = "org.coordinate";
    private static final String POINTS_COUNTER_NAME = DOMAIN + ":type=PointsCounter";
    private static final String CLICK_INTERVAL_NAME = DOMAIN + ":type=ClickInterval";

    private PointsCounter pointsCounter;
    private ClickInterval clickInterval;

    @PostConstruct
    public void init() {
        try {
            MBeanServer mbs = ManagementFactory.getPlatformMBeanServer();

            pointsCounter = new PointsCounter();
            ObjectName pointsName = new ObjectName(POINTS_COUNTER_NAME);
            mbs.registerMBean(pointsCounter, pointsName);

            clickInterval = new ClickInterval();
            ObjectName intervalName = new ObjectName(CLICK_INTERVAL_NAME);
            mbs.registerMBean(clickInterval, intervalName);

            LOGGER.info("[JMX] MBeans registered: "
                    + POINTS_COUNTER_NAME + ", " + CLICK_INTERVAL_NAME);
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "[JMX] Failed to register MBeans: " + e.getMessage(), e);
        }
    }

    @PreDestroy
    public void destroy() {
        try {
            MBeanServer mbs = ManagementFactory.getPlatformMBeanServer();
            mbs.unregisterMBean(new ObjectName(POINTS_COUNTER_NAME));
            mbs.unregisterMBean(new ObjectName(CLICK_INTERVAL_NAME));
            LOGGER.info("[JMX] MBeans unregistered.");
        } catch (Exception e) {
            LOGGER.log(Level.WARNING, "[JMX] Failed to unregister MBeans: " + e.getMessage());
        }
    }

    public PointsCounter getPointsCounter() {
        return pointsCounter;
    }

    public ClickInterval getClickInterval() {
        return clickInterval;
    }
}
