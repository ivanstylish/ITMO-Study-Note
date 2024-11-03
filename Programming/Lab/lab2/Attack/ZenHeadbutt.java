package Attack;

import ru.ifmo.se.pokemon.Effect;
import ru.ifmo.se.pokemon.PhysicalMove;
import ru.ifmo.se.pokemon.Pokemon;
import ru.ifmo.se.pokemon.Type;

public class ZenHeadbutt extends PhysicalMove {
    public ZenHeadbutt(){
        super(Type.PSYCHIC, 80.0, 90.0);
    }

    @Override
    protected void applyOppEffects(Pokemon p) {
        if (Math.random() < 0.2) {
            Effect.flinch(p);
        }
    }

    @Override
    protected String describe() {
        return "uses " + this.getClass().getSimpleName() + " ,make the enemy to flinch."; // 返回此类的简单的名称
    }
}
