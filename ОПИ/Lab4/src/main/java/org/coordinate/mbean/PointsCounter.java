package org.coordinate.mbean;

import javax.management.Notification;
import javax.management.NotificationBroadcasterSupport;

/**
 * MBean implementation that counts total points, hit points,
 * and sends JMX notifications when a point is placed outside the
 * visible coordinate plane area.
 */
public class PointsCounter extends NotificationBroadcasterSupport
        implements PointsCounterMBean {

    private long totalPoints;
    private long hitPoints;
    private long outOfBoundsPoints;
    private long notificationSequence;

    // Visible area boundaries on the coordinate plane canvas
    public static final double BOUNDS_X = 5.0;
    public static final double BOUNDS_Y = 5.0;

    @Override
    public long getTotalPoints() {
        return totalPoints;
    }

    @Override
    public long getHitPoints() {
        return hitPoints;
    }

    @Override
    public long getOutOfBoundsPoints() {
        return outOfBoundsPoints;
    }

    @Override
    public void resetCounters() {
        totalPoints = 0;
        hitPoints = 0;
        outOfBoundsPoints = 0;
    }

    /**
     * Record a point check and optionally send notification.
     *
     * @param x   X coordinate of the point
     * @param y   Y coordinate of the point
     * @param hit whether the point fell into the area
     */
    public synchronized void recordPoint(double x, double y, boolean hit) {
        totalPoints++;
        if (hit) {
            hitPoints++;
        }

        if (isOutOfBounds(x, y)) {
            outOfBoundsPoints++;
            sendOutOfBoundsNotification(x, y);
        }
    }

    private boolean isOutOfBounds(double x, double y) {
        return Math.abs(x) > BOUNDS_X || Math.abs(y) > BOUNDS_Y;
    }

    private void sendOutOfBoundsNotification(double x, double y) {
        Notification notif = new Notification(
                "out.of.bounds",
                this,
                notificationSequence++,
                System.currentTimeMillis(),
                String.format("Point (%.2f, %.2f) is outside visible area (+/-%.0f)", x, y, BOUNDS_X)
        );
        sendNotification(notif);
    }
}
