package Characters;

import Characters.Enums.Emotion;
import MyException.InvalidCharacterStateException;

public abstract class Character {
    protected boolean isLookingIntoMirror;
    protected CharacterInfo info;

    public Character(CharacterInfo info) {
        this.info = info;
        this.isLookingIntoMirror = false;
    }

    public void changeEmotion(Emotion newEmo){
        System.out.println(this.info.name() + " чувствует сейчас " + newEmo.getDescription() + ".");
    }
    public abstract void reactToMirror() throws InvalidCharacterStateException;

    @Override
    public String toString() {
        return "Его зовут " + info.name() + " " + info.gender().getForm() + " [" + "первоначальная эмоция: " + info.emotion().getDescription() + "]";
    }

    @Override
    public int hashCode() {
        return info.hashCode();
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj){
            return true;
        }if (obj == null || getClass() != obj.getClass()){
            return false;
        }
        Character character = (Character) obj;
        return info.equals(character.info);
    }
}
