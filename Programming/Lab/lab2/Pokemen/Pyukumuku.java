package Pokemen;

import Attack.Confide;
import Attack.Harden;
import Attack.Recover;
import Attack.Swagger;
import ru.ifmo.se.pokemon.Pokemon;
import ru.ifmo.se.pokemon.Type;

public class Pyukumuku extends Pokemon {
    public Pyukumuku(String name, int level){
        super(name, level);
        this.setType(Type.WATER);
        this.setStats(55.0, 60.0, 130.0, 30.0, 130.0, 5.0);
        Swagger attack1 = new Swagger();
        Harden attack2 = new Harden();
        Confide attack3 = new Confide();
        Recover attack4 = new Recover();
        this.setMove(attack1, attack2, attack3, attack4);
    }
}
