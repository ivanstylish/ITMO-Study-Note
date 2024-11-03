package Items;

import Interfaces.Reflectable;

public class Mirror implements Reflectable {
    protected String name = "зеркало";
    public String getMirrorName(){
        return name;
    }

    @Override
    public String reflectLight() {
        return "маленькое зеркальце, которым он обычно пускал солнечных зайчиков.";
    }

}
