package Characters;

import Characters.Enums.Emotion;
import Characters.Enums.Gender;
import Characters.Enums.Move;
import Items.Mirror;
import Items.Pocket;
import MyException.InvalidCharacterStateException;

public class Cipollino extends Character {
    public Cipollino(){
        super(new CharacterInfo("Чиполлино", Gender.Male, Emotion.CALM));
    }



    public void UseMirror(Mirror mirror, MrTomato mrTomato) throws InvalidCharacterStateException{
        System.out.println(this.info.name() + Move.took_out.getDescription() + "маленькое зеркало и" + Move.twirled.getDescription() + "перед " + mrTomato.info.name() + ".");
        mirror.reflectLight();

        mrTomato.setLookingIntoMirror(true);
        try {
            if (mrTomato.isEnhanced()) {
                mrTomato.reflectToAction();
                mrTomato.reactToMirror();

            } else {
                throw new InvalidCharacterStateException(mrTomato.info.name() + " находится в улучшенном состоянии. Не может пользоваться зеркалом.");
            }
        } finally {
            // 无论如何都要重置状态
            mrTomato.setLookingIntoMirror(false);
        }
    }
    public String ci_name(){
        return info.name();
    }
    public void approach(Cipollino cipollino, Pocket pocket){
        System.out.println(cipollino.info.name() + Move.holded_out_a_hand.getDescription() + pocket.storable());
    }
    public void tookout(Mirror mirror){
        System.out.println("он" + Move.took_out.getDescription() + mirror.reflectLight());
    }
    public void move(MrTomato tomato){
        System.out.println("он" + Move.approached.getDescription() + tomato.info.name());
    }

    public void move1(MrTomato tomato, Mirror mirror){
        System.out.println(tomato.info.name() + Move.tempted.getDescription() + "и" + Move.looked_towards.getDescription() + mirror.getMirrorName());
    }
    @Override
    public void reactToMirror() throws InvalidCharacterStateException {
        System.out.println(this.info.name() + Emotion.PROUD + " улыбается.");
    }
}
