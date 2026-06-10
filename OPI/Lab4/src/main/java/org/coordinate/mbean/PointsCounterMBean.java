package org.coordinate.mbean;

/**
 * MBean interface for counting points.
 * Tracks total number of points set by the user and points that hit the area.
 * Sends notification when coordinates go beyond the visible coordinate plane.
 */
public interface PointsCounterMBean {

    /** @return total number of points ever set by the user */
    long getTotalPoints();

    /** @return number of points that hit the area */
    long getHitPoints();

    /** @return count of out-of-bounds points */
    long getOutOfBoundsPoints();

    /** Reset all counters to zero */
    void resetCounters();
}
