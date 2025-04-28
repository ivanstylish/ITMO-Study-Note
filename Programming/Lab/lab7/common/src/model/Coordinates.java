package model;

import java.io.Serializable;
import java.util.Objects;

public class Coordinates implements Serializable {
    private double x; //Значение поля должно быть больше -401
    private float y; //Максимальное значение поля: 569

    public Coordinates(double x, float y) {
        this.setX(x);
        this.setY(y);
    }

    public double getX() {
        return x;
    }

    public float getY() {
        return y;
    }

    /**
     * print the information of coordination
     *
     * @return String
     */
    @Override
    public String toString() {
        return String.format("Coordinates{x=" + x + " , " + "y=" + y + "}");
    }


    @Override
    public int hashCode() {
        return Objects.hash(x, y);
    }

    public void setX(double x) {
        if (x <= -401) {
            throw new IllegalArgumentException("Coordinates.x must be > -401");
        }
        this.x = x;
    }

    public void setY(float y) {
        if (y > 569) {
            throw new IllegalArgumentException("Coordinates.y must be <= 569");
        }
        this.y = y;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Coordinates that = (Coordinates) o;
        return Double.compare(that.x, x) == 0 &&
                Float.compare(that.y, y) == 0;
    }
}
