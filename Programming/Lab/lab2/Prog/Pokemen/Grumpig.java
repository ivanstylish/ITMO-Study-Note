package Pokemen;

import Attack.ConfuseRay;
import Attack.EnergyBall;
import Attack.Rest;
import ru.ifmo.se.pokemon.Pokemon;
import ru.ifmo.se.pokemon.Type;
import Attack.ZenHeadbutt;

public class Grumpig extends Pokemon{
    public Grumpig(String name, int level){
        super(name, level); // 指向当前对象的父类
        this.setType(Type.PSYCHIC); // 指向对象本身的类型
        this.setStats(80.0, 45.0, 65.0, 90.0, 110.0, 80.0);
        ZenHeadbutt attack1 = new ZenHeadbutt();
        Rest attack2 = new Rest();
        ConfuseRay attack3 = new ConfuseRay();
        EnergyBall attack4 = new EnergyBall();
        this.setMove(attack1, attack2, attack3, attack4);

    }
}
