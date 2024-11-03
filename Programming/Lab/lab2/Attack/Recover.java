package Attack;

import ru.ifmo.se.pokemon.Pokemon;
import ru.ifmo.se.pokemon.Stat;
import ru.ifmo.se.pokemon.StatusMove;
import ru.ifmo.se.pokemon.Type;

public class Recover extends StatusMove {
    public Recover(){
        super(Type.NORMAL, 0.0, 0.0);
    }

    @Override
    protected void applySelfEffects(Pokemon p) {
        double recoverAmount = p.getStat(Stat.HP) * 0.5; // 恢复用户最大生命值的50%
        p.setMod(Stat.HP, (int)recoverAmount);
    }

    @Override
    protected String describe() {
        return "uses " + getClass().getSimpleName() + " ,and recover itself for 50% HP.";
    }
}
