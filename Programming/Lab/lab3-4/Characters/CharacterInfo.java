package Characters;

import Characters.Enums.Emotion;
import Characters.Enums.Gender;

public record CharacterInfo(String name, Gender gender, Emotion emotion) {
}
