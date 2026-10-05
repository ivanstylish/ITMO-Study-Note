package org.coordinate.mbean;

/**
 * MBean interface for tracking average interval between user clicks
 * on the coordinate plane.
 */
public interface ClickIntervalMBean {

    /** @return average interval between clicks in milliseconds */
    double getAverageIntervalMs();

    /** @return total number of clicks recorded */
    long getTotalClicks();

    /** @return the last click interval in milliseconds, or 0 if fewer than 2 clicks */
    long getLastIntervalMs();

    /** Reset all interval statistics */
    void resetIntervals();
}
