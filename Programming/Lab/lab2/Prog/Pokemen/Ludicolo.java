package Pokemen;

import Attack.Blizzard;
import Attack.Bubble;
import Attack.SwordsDance;
import Attack.Waterfall;
import ru.ifmo.se.pokemon.Pokemon;
import ru.ifmo.se.pokemon.Type;

public class Ludicolo extends Pokemon {
    public Ludicolo(String name, int level){
        super(name, level);
        this.setType(Type.WATER, Type.GRASS);
        this.setStats(80.0, 70.0, 70.0, 90.0, 100.0, 70.0);
        Blizzard attack1 = new Blizzard();
        SwordsDance attack2 = new SwordsDance();
        Bubble attack3 = new Bubble();
        Waterfall attack4 = new Waterfall();
        this.setMove(attack1, attack2, attack3, attack4);
    }
}
