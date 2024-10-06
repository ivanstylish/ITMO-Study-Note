package Pokemen;

import Attack.Blizzard;
import Attack.SwordsDance;
import ru.ifmo.se.pokemon.Pokemon;
import ru.ifmo.se.pokemon.Type;

public class Lotad extends Pokemon {
    public Lotad(String name, int level){
        super(name, level);
        this.setType(Type.WATER, Type.GRASS);
        this.setStats(40.0, 30.0, 30.0, 40.0, 50.0, 30.0);
        Blizzard attack1 = new Blizzard();
        SwordsDance attack2 = new SwordsDance();
        this.setMove(attack1, attack2);
    }
}
