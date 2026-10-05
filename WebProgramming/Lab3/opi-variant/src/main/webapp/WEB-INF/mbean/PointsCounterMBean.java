package org.coordinate.mbean;

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
