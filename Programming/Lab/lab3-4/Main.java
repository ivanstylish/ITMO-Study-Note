import Characters.Character;
import Characters.Cipollino;
import Characters.MrTomato;
import Environment.RainyDay;
import Environment.Street;
import Environment.SunnyDay;
import Environment.WeatherChange;
import Items.Mirror;
import Items.Pocket;
import MyException.InputException;
import MyException.InvalidCharacterStateException;

import java.util.ArrayList;

public class Main {
    public static void main(String[] args) {
        System.out.println("NOW INTRODUCE THE CHARACTERS, AND THE ENVIRONMENT: ");

        ArrayList<Character> characters = new ArrayList<>();
        Cipollino cipollino = new Cipollino();
        MrTomato tomato = new MrTomato(5);
        characters.add(cipollino);
        characters.add(tomato);
        Mirror mirror = new Mirror();
        Pocket pocket = new Pocket();

        for (Character character : characters){
            System.out.println(character.toString());
        }
        System.out.println();

        SunnyDay sunnyDay = new SunnyDay();
        RainyDay rainyDay = new RainyDay();
        WeatherChange weather = new WeatherChange();
        Street street = new Street();

        System.out.println("Это был " + sunnyDay);
        sunnyDay.affectCharacter();
        System.out.print(street);
        street.fact(cipollino, tomato);
        cipollino.approach(cipollino, pocket);
        cipollino.tookout(mirror);

        cipollino.move(tomato);
        cipollino.move1(tomato, mirror);
        try{
            cipollino.UseMirror(mirror, tomato);
        }catch (InvalidCharacterStateException e){
            System.out.println(e.getMessage());
        }
        weather.processOfChangeW(tomato);
        rainyDay.affectCharacter();
        try {
            weather.guessTomatoEmo();
            } catch (InputException e) {
            System.out.println(e.getDescription());
            }

        System.out.println("----------- Конец истории, спасибо за просмотр!! -----------");
        }
    }

