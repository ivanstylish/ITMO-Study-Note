
//
// Created by 26771 on 2025/9/12.
// Modified to use predefined text and key
//
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 函数原型
void encrypt(char* text, int key);
void decrypt(char* text, int key);

int main() {
    // 预设的文本和密钥
    char original_text[] = "Hello";
    int key = 21;

    char encrypted_text[strlen(original_text) + 1];
    strcpy(encrypted_text, original_text);

    char decrypted_text[strlen(original_text) + 1];

    printf("=== Caesar ===\n");
    printf("Text: %s\n", original_text);
    printf("key: %d\n", key);
    printf("\n");

    encrypt(encrypted_text, key);
    printf("Encrypted: %s\n", encrypted_text);
    printf("\n");

    strcpy(decrypted_text, encrypted_text);
    decrypt(decrypted_text, key);
    printf("Discrypted: %s\n", decrypted_text);
    printf("\n");

    return 0;
}

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
            char shiftedChar = 'a' + (currentChar - 'a' - key + 26) % 26;
            text[i] = shiftedChar;
        }
        else if (currentChar >= 'A' && currentChar <= 'Z') {
            char shiftedChar = 'A' + (currentChar - 'A' - key + 26) % 26;
            text[i] = shiftedChar;
        }
    }
}