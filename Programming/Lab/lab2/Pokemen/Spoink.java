package Pokemen;

import Attack.ConfuseRay;
import Attack.Rest;
import Attack.ZenHeadbutt;
import ru.ifmo.se.pokemon.Pokemon;
import ru.ifmo.se.pokemon.Type;

public class Spoink extends Pokemon {
    public Spoink(String name, int level){
        super(name, level);
        this.setType(Type.PSYCHIC);
        this.setStats(60.0,25.0, 35.0, 70.0, 80.0, 60.0);
        ZenHeadbutt attack1 = new ZenHeadbutt();
        Rest attack2 = new Rest();
        ConfuseRay attack3 = new ConfuseRay();
        this.setMove(attack1, attack2, attack3);
    }
}
