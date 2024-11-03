package Characters;
import Characters.Enums.Emotion;
import Characters.Enums.Gender;
import MyException.InvalidCharacterStateException;

public class MrTomato extends Character {
    private int prideLevel;
    private boolean isEnhanced = true;
    public MrTomato(int prideLevel){
        super(new CharacterInfo("синьор Помидор", Gender.Male, Emotion.ANGRY));
        this.prideLevel = prideLevel;
    }
    public boolean isEnhanced() {
        return this.isEnhanced;
    }
    public String to_name(){
        return info.name();
    }
    public String to_emo(){
        return info.emotion().getDescription();
    }

    public void reflectToAction(){
        if (prideLevel > 4){
            this.changeEmotion(Emotion.ANGRY);
        }else {
            this.changeEmotion(Emotion.CALM);
        }
    }

    public void setLookingIntoMirror(boolean isLookingIntoMirror) {
        this.isLookingIntoMirror = isLookingIntoMirror;
    }

    @Override
    public void reactToMirror() throws InvalidCharacterStateException {
        if (this.isLookingIntoMirror) {
            System.out.println(info.name() + " увидел только свою собственную красную, как огонь, физиономию со злыми маленькими глазками и большим ртом, похожим на прорезь копилки.");
            throw new InvalidCharacterStateException("синьора Помодоро усилился из-за его отражения!");
        }else {
            System.out.println(info.name() + " отказался смотреться в зеркало.");
        }
    }
}
