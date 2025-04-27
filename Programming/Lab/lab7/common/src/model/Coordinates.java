package model;

import java.util.Objects;

public class Coordinates {
    private double x; //Значение поля должно быть больше -401
    private float y; //Максимальное значение поля: 569


    public double getX(){
        return x;
    }

    public float getY() {
        return y;
    }

    /**
     * print the information of coordination
     * @return String
     */
    @Override
    public String toString() {
        return String.format("Coordinates{x=" + x + " , " + "y=" + y + "}");
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Coordinates that = (Coordinates) o;
        return Objects.equals(x, that.x) && Objects.equals(y, that.y);
    }

    @Override
    public int hashCode() {
        return Objects.hash(x, y);
    }

    public void setX(double x) {
        this.x = x;
    }

    public void setY(float y) {
        this.y = y;
    }
}