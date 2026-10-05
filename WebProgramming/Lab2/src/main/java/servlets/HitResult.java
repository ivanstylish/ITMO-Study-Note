package servlets;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class HitResult {
    private final double x, y ,r;
    private final boolean hit;
    private final String time;
    private final long duration;

    public HitResult(double x, double y, double r, boolean hit, long duration)
    {
        this.x = x;
        this.y = y;
        this.r = r;
        this.hit = hit;
        this.duration = duration;
        this.time = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
    }

    public double getX() {
        return x;
    }

    public double getY() {
        return y;
    }

    public double getR() {
        return r;
    }

    public boolean isHit() {
        return hit;
    }

    public long getDuration() {
        return duration;
    }

    public String getTime() {
        return time;
    }
}
