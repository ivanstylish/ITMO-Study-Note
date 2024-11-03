package Attack;
import ru.ifmo.se.pokemon.*;

public class Rest extends StatusMove{
    public Rest(){
        super(Type.PSYCHIC, 0.0, 0.0);
    }

    @Override
    protected void applySelfEffects(Pokemon p) {
        p.setMod(Stat.HP, (int) -(p.getStat(Stat.HP) - p.getHP())); // 最大hp值减当前hp值
        Effect e = new Effect().turns(2).condition(Status.SLEEP);
        p.addEffect(e);
    }

    @Override
    protected String describe() {
        return "uses " + this.getClass().getSimpleName() + " ,and falls asleep for 2 turns, but is fully healed!"; // 返回此类的简单的名称
    }
}
