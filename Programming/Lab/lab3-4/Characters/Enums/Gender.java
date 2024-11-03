package Characters.Enums;

public enum Gender {
    Male("мужчина");


    private final String form;
    Gender(String form){
        this.form = form;
    }
    public String getForm(){
        return form;
    }
}
