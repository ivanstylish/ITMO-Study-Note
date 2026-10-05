package org.coordinate.mbean;

/**
 * MBean implementation that calculates the average interval
 * between consecutive user clicks on the coordinate plane.
 */
public class ClickInterval implements ClickIntervalMBean {

    private long totalClicks;
    private long lastClickTimestampMs;
    private double totalIntervalsMs;
    private long lastIntervalMs;

    @Override
    public synchronized double getAverageIntervalMs() {
        if (totalClicks < 2) {
            return 0.0;
        }
        return totalIntervalsMs / (totalClicks - 1);
    }

    @Override
    public long getTotalClicks() {
        return totalClicks;
    }

    @Override
    public long getLastIntervalMs() {
        return lastIntervalMs;
    }

    @Override
    public synchronized void resetIntervals() {
        totalClicks = 0;
        lastClickTimestampMs = 0;
        totalIntervalsMs = 0;
        lastIntervalMs = 0;
    }

    /**
     * Record a click and update interval statistics.
     */
    public synchronized void recordClick() {
        long now = System.currentTimeMillis();
        totalClicks++;

        if (lastClickTimestampMs > 0) {
            lastIntervalMs = now - lastClickTimestampMs;
            totalIntervalsMs += lastIntervalMs;
        }

        lastClickTimestampMs = now;
    }
}
