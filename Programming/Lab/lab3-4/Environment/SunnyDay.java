package Environment;

public class SunnyDay extends Place{
    public SunnyDay() {
        super("Солнечный день");
    }

    public void affectCharacter() {
        System.out.println("Ярко светит солнце. Персонажи могут чувствовать себя более энергичными.");
    }
}
