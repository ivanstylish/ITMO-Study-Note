package org.coordinate.bean;

import org.coordinate.entity.Result;

import java.io.Serializable;

public class ResultDTO implements Serializable {
    private final Double x;
    private final Double y;
    private final Double r;
    private final Boolean hit;
    private final String timestamp;
    private final Long executionTime;

    public ResultDTO(Result r) {
        this.x = r.getX();
        this.y = r.getY();
        this.r = r.getR();
        this.hit = r.getHit();
        this.timestamp = r.getCheckTime().format(ResultBean.FORMATTER);
        this.executionTime = r.getExecutionTime();
    }

    public Double getX() { return x; }
    public Double getY() { return y; }
    public Double getR() { return r; }
    public Boolean getHit() { return hit; }
    public String getTimestamp() { return timestamp; }
    public Long getExecutionTime() { return executionTime; }
}