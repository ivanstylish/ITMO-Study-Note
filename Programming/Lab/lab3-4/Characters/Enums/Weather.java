package Characters.Enums;

public enum Weather {
    SUNNY("Солнчный день"),
    CLOUDY("облачный день"),
    RAINY("дождливый день");

    private final String description;
    Weather(String description){
        this.description = description;
    }

    @Override
    public String toString() {
        return description;
    }
}
