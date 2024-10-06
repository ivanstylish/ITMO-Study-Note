package Attack;

import ru.ifmo.se.pokemon.Effect;
import ru.ifmo.se.pokemon.PhysicalMove;
import ru.ifmo.se.pokemon.Pokemon;
import ru.ifmo.se.pokemon.Type;

public class Waterfall extends PhysicalMove {
    public Waterfall(){
        super(Type.WATER, 80.0, 100.0);
    }

    @Override
    protected void applyOppEffects(Pokemon p) {
        if (Math.random() < 0.2){
            Effect.flinch(p);
        }
    }

    @Override
    protected String describe() {
        return "uses " + getClass().getSimpleName() + " ,and causes the enemy to finch.";
    }
}
