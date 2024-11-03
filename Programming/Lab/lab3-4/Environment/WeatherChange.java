package Environment;

import Characters.Enums.Emotion;
import Characters.Enums.Weather;
import Characters.MrTomato;
import MyException.InputException;

import java.util.Scanner;


public class WeatherChange {
    private String currentWeather;

    public WeatherChange() {
        this.currentWeather = Weather.SUNNY.toString();
    }

    public void processOfChangeW(MrTomato tomato) {
        System.out.println("Сейчас погода " + currentWeather + ".");
        System.out.println("По мере того как синьор Помидор становится злым, погода начинает меняться...");

        while (tomato.to_emo().equals(Emotion.ANGRY.getDescription())) {
            this.currentWeather = Weather.CLOUDY.toString();
            System.out.println("Погода переходит в " + currentWeather + ".");
            System.out.println("Внезапно тучи потемнели, и небо стало пасмурным.");
            break;
        }
        if (currentWeather.equals(Weather.CLOUDY.toString())) {
            System.out.println("Начинает капать дождь...");
            this.currentWeather = Weather.RAINY.toString();
            System.out.println("Теперь погода " + currentWeather + ".");
        }
    }
    public void guessTomatoEmo() throws InputException {
        String guess1 = Emotion.SAD.getDescription();
        String guess2 = Emotion.HAPPY.getDescription();

        Scanner scanner = new Scanner(System.in);
        System.out.println("Please enter ur suppose: Now how Mr. Tomato is feeling (Please enter 'грустно' or 'радостно')");

        String suppose = scanner.nextLine();
        if (!suppose.equals(guess1) && !suppose.equals(guess2)){
            throw new InputException("Input Error! Please enter 'грустно' or 'радостно'.");
        }
        if (suppose.equals(guess1)){
            System.out.println("Congrats!!! Вы угадали! Помидору сейчас грустно.");
        }else {
            System.out.println("К сожалению, сейчас ему не радостно.");
        }
    }
}