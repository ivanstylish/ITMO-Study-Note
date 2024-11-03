package Attack;

import ru.ifmo.se.pokemon.*;

public class EnergyBall extends SpecialMove {
    public EnergyBall(){
        super(Type.GRASS, 90.0, 100.0);
    }

    @Override
    protected void applyOppEffects(Pokemon p) {
        Effect e = new Effect().chance(0.1).stat(Stat.SPECIAL_DEFENSE, -1);
        p.addEffect(e);
    }
    @Override
    protected String describe() {
        return "uses " + this.getClass().getSimpleName(); // 返回此类的简单的名称
    }

}
