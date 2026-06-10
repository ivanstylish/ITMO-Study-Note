package org.coordinate.mbean;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Named;

import javax.management.MBeanServer;
import javax.management.ObjectName;
import java.lang.management.ManagementFactory;

/**
 * Startup bean that registers application MBeans with the platform MBean server.
 */
@Named("JMXRegistration")
@ApplicationScoped
public class JMXRegistration {

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

            System.out.println("[JMX] MBeans registered: "
                    + POINTS_COUNTER_NAME + ", " + CLICK_INTERVAL_NAME);
        } catch (Exception e) {
            System.err.println("[JMX] Failed to register MBeans: " + e.getMessage());
            e.printStackTrace();
        }
    }

    @PreDestroy
    public void destroy() {
        try {
            MBeanServer mbs = ManagementFactory.getPlatformMBeanServer();
            mbs.unregisterMBean(new ObjectName(POINTS_COUNTER_NAME));
            mbs.unregisterMBean(new ObjectName(CLICK_INTERVAL_NAME));
            System.out.println("[JMX] MBeans unregistered.");
        } catch (Exception e) {
            System.err.println("[JMX] Failed to unregister MBeans: " + e.getMessage());
        }
    }

    public PointsCounter getPointsCounter() {
        return pointsCounter;
    }

    public ClickInterval getClickInterval() {
        return clickInterval;
    }
}
