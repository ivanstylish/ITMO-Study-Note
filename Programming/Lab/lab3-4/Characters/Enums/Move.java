package Characters.Enums;


public enum Move {
    holded_out_a_hand(" засунул руку в "),
    took_out(" вытащил "),
    approached(" подощёл к "),
    twirled(" повертел "),
    looked_towards(" посмотрел в "),
    tempted(" не удержался от искушения "),
    saw(" увидел ");

    private final String text;


    Move(String text){
        this.text = text;
    }

    public String getDescription() {
        return text;
    }
}
