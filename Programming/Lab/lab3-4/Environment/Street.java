package Environment;

import Characters.Cipollino;
import Characters.Enums.Move;
import Characters.MrTomato;

public class Street extends Place{

    public Street() {
        super("На незнакомой улице ");
    }
    public void fact(Cipollino cipollino, MrTomato tomato){
        System.out.println(cipollino.ci_name() + Move.saw.getDescription() + tomato.to_name() + ".");
    }
}
