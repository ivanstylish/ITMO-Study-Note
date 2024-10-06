package Attack;

import ru.ifmo.se.pokemon.*;

public class Blizzard extends SpecialMove {
    public Blizzard(){
        super(Type.ICE, 110.0, 70.0);
    }

    @Override
    protected void applyOppEffects(Pokemon p) {
        if (!p.hasType(Type.ICE)){
            if (Math.random() < 0.1){
                Effect.freeze(p);
            }
        }
    }
    @Override
    protected boolean checkAccuracy(Pokemon att, Pokemon def) {
        return super.checkAccuracy(att, def);
    }

    @Override
    protected String describe() {
        return "uses " + getClass().getSimpleName() + " ,and has a 10% chance to freeze the target. Ignores hit points in hailstorms.";
    }
}
