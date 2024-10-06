package Attack;

import ru.ifmo.se.pokemon.*;

public class Harden extends StatusMove {
    public Harden(){
        super(Type.NORMAL, 0.0, 0.0);
    }

    @Override
    protected void applySelfEffects(Pokemon p) {
        p.setMod(Stat.DEFENSE, 1);
    }

    @Override
    protected String describe() {
        return "uses " + getClass().getSimpleName() + " ,makes itself Defense higher by one stage.";
    }
}
