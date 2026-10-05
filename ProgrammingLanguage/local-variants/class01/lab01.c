
#include <stdio.h>
#include <stdlib.h>

// Прототип функции шифрования
void encrypt(char* text, int key);
void decrypt(char* text, int key);
int main(int argc, char* argv[]) {
    if (argc != 3) {
        printf("Usage: ./caesar <key>\n");
        return 1;
    }

    char* text = argv[1];
    int key = atoi(argv[2]);

    printf("Source text: %s\n", text);
    printf("Key: %d\n", key);

    // Вызываем функцию для выполнения шифрования
    encrypt(text, key);

    printf("Encrypted text: %s\n", text);

    decrypt(text, key);

    printf("Decrypted text: %s\n", text);

    return 0;
}

// Реализация функции шифрования
void encrypt(char text[], int key) {
    for (int i = 0; text[i] != '\0'; i++) {
        char currentChar = text[i];

        if (currentChar >= 'a' && currentChar <= 'z') {
            char shiftedChar = 'a' + (currentChar - 'a' + key) % 26;
            text[i] = shiftedChar;
        }
        else if (currentChar >= 'A' && currentChar <= 'Z') {
            char shiftedChar = 'A' + (currentChar - 'A' + key) % 26;
            text[i] = shiftedChar;
        }
    }
}


void decrypt(char text[], int key) {
    for (int i = 0; text[i] != '\0'; i++) {
        char currentChar = text[i];

        if (currentChar >= 'a' && currentChar <= 'z') {

            int shift = (currentChar - 'a' - key) % 26;

            if (shift < 0) {
                shift += 26;
            }
            char originalChar = 'a' + shift;
            text[i] = originalChar;
        } else if (currentChar >= 'A' && currentChar <= 'Z') {
            int shift = (currentChar - 'A' - key) % 26;
            if (shift < 0) {
                shift += 26;
            }
            char originalChar = 'A' + shift;
            text[i] = originalChar;
        }
    }
}

