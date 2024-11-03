package Environment;

public abstract class Place {
    protected String placeName;

    protected Place(String placeName) {
        this.placeName = placeName;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj){
            return true;
        } else if (obj == null || obj.getClass() != getClass()) {
            return false;
        }
        Place place = (Place) obj;
        return this.placeName.equals(place.placeName);
    }

    @Override
    public String toString() {
        return this.placeName;
    }


}
