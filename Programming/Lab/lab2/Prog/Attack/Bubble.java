package Attack;

import ru.ifmo.se.pokemon.*;

public class Bubble extends SpecialMove {
    public Bubble(){
        super(Type.WATER, 40.0, 100.0);
    }

    @Override
    protected void applyOppEffects(Pokemon p) {
        Effect e = new Effect().chance(0.1).stat(Stat.SPEED, -1);
        p.addEffect(e);
    }

    @Override
    protected String describe() {
        return "uses " + getClass().getSimpleName() + " ,and get enemy's Speed lower by one stage.";
    }
}
