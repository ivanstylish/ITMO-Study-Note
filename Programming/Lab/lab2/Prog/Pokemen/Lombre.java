package Pokemen;

import Attack.Blizzard;
import Attack.Bubble;
import Attack.SwordsDance;
import ru.ifmo.se.pokemon.Pokemon;
import ru.ifmo.se.pokemon.Type;

public class Lombre extends Pokemon {
    public Lombre(String name, int level){
        super(name, level);
        this.setType(Type.WATER, Type.GRASS);
        this.setStats(60.0, 50.0, 50.0, 60.0, 70.0, 50.0);
        Blizzard attack1 = new Blizzard();
        SwordsDance attack2 = new SwordsDance();
        Bubble attack3 = new Bubble();
        this.setMove(attack1, attack2, attack3);
    }
}
