package Attack;

import ru.ifmo.se.pokemon.*;

public class ConfuseRay extends StatusMove {
    public ConfuseRay() {
        super(Type.GHOST, 0.0, 100.0);
    }

    @Override
    protected void applyOppEffects(Pokemon p) {
        double baseDamage = 40.0;
        Effect.confuse(p);
        if (Math.random() < 0.33){
            System.out.println("It hurts ifself " + baseDamage + "damage.");
        }
    }

    @Override
    protected String describe() {
        return "uses " + this.getClass().getSimpleName(); // 返回此类的简单的名称
    }
}
