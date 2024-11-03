package Characters.Enums;

public enum Emotion {
    ANGRY("сердито"),
    CALM("спокойно"),
    PROUD(" гордо"),
    SAD("грустно"),
    HAPPY("радостно");

    private final String description;
    Emotion(String description){
        this.description = description;
    }

    public String getDescription() {
        return description;
    }
}
