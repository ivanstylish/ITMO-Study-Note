package model;

import java.io.Serializable;
import java.util.Objects;

public class Coordinates implements Serializable {
    private double x; //Значение поля должно быть больше -401
    private float y; //Максимальное значение поля: 569

    public Coordinates(double x, float y) {
        this.x = x;
        this.y = y;
    }
    public double getX(){
        return x;
    }

    public float getY(){
        return y;
    }

    @Override
    public int hashCode() {
        return Objects.hash(x, y);
    }

    @Override
    public String toString() {
        return String.format("Coordinates{x=" + x + " , " + "y=" + y + "}");
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) {
            return true;
        }
        if (obj == null ||getClass() != obj.getClass()) {
            return false;
        }
        Coordinates that = (Coordinates) obj;
        return Objects.equals(x, that.x) && Objects.equals(y, that.y);
    }
}
