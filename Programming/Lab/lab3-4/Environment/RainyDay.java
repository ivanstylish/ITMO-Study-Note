package Environment;

public class RainyDay extends Place{
    public RainyDay(){
        super("Дождливый день");
    }

    public void affectCharacter() {
        System.out.println("Дождливый день. Персонажи могут чувствовать себя мрачными и сонными.");
    }
}
