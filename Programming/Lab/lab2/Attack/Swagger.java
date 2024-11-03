package Attack;

import ru.ifmo.se.pokemon.*;

public class Swagger extends StatusMove{
    public Swagger() {
        super(Type.NORMAL, 0.0, 85.0);
    }

    @Override
    protected void applyOppEffects(Pokemon p) {
        p.setMod(Stat.ATTACK, 2);
        Effect.confuse(p);
    }

    @Override
    protected String describe() {
        return "uses " + getClass().getSimpleName() + " ,try to raise enemy's Attack and confuses him.";
    }
}
