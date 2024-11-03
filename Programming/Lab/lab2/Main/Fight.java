package Main;

import Pokemen.*;
import ru.ifmo.se.pokemon.Battle;

public class Fight {
    public static void main(String[] args) {
        Battle battle = new Battle();
        battle.addAlly(new Pyukumuku("Lil wolf", 20));
        battle.addAlly(new Spoink("Med wolf", 40));
        battle.addAlly(new Grumpig("Big wolf", 60));

        battle.addFoe(new Lotad("Lil tiger", 20));
        battle.addFoe(new Lombre("Med tiger", 40));
        battle.addFoe(new Ludicolo("Big tiger", 60));
        battle.go();
    }
}
