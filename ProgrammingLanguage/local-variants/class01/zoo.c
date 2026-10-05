//
// Created by 26771 on 2025/9/26.
//
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

typedef struct {
    double x;
    double y;
} Position;

typedef enum {
    MAMMAL,
    BIRD,
    REPTILE,
    FISH
} ANIMAL_TYPE;

typedef enum {
    MALE,
    FEMALE,
    UNKNOWN
} SEX;

typedef struct {
    char name[20];
    int age;
    double height;
    double weight;
    SEX sex;
    ANIMAL_TYPE type;
    Position position;
    int hunger;
    int happiness;
} Animal;

const char* animal_names[] = {"Leo", "Bella", "Max", "Luna", "Charlie", "Daisy", "Rocky", "Zoe"};
const char* type_names[] = {"Mammal", "Bird", "Reptile", "Fish"};
const char* sex_names[] = {"Male", "Female", "Unknown"};

Position createRandomPosition() {
    Position pos;
    pos.x = (double)(rand() % 100) / 10.0;
    pos.y = (double)(rand() % 100) / 10.0;
    return pos;
}

Animal* createAnimal(const char* name, int age, double height, double weight, SEX sex, ANIMAL_TYPE type) {
    Animal* animal = malloc(sizeof(Animal));
    if (!animal) return NULL;

    strcpy(animal->name, name);
    animal->age = age;
    animal->height = height;
    animal->weight = weight;
    animal->sex = sex;
    animal->type = type;
    animal->position = createRandomPosition();
    animal->hunger = 50 + rand() % 30;
    animal->happiness = 60 + rand() % 30;

    return animal;
}

Animal* createRandomAnimal() {
    const char* name = animal_names[rand() % 8];
    int age = 1 + rand() % 15;
    double height = 0.5 + (double)(rand() % 300) / 100.0;
    double weight = 5.0 + (double)(rand() % 200) / 10.0;
    SEX sex = rand() % 3;
    ANIMAL_TYPE type = rand() % 4;

    return createAnimal(name, age, height, weight, sex, type);
}

void printAnimal(const Animal* animal) {
    if (!animal) {
        printf("Invalid animal\n");
        return;
    }

    printf("=================\n");
    printf("Name: %s\n", animal->name);
    printf("Age: %d years\n", animal->age);
    printf("Height: %.2f m\n", animal->height);
    printf("Weight: %.2f kg\n", animal->weight);
    printf("Type: %s\n", type_names[animal->type]);
    printf("Sex: %s\n", sex_names[animal->sex]);
    printf("Position: (%.1f, %.1f)\n", animal->position.x, animal->position.y);
    printf("Hunger: %d/100\n", animal->hunger);
    printf("Happiness: %d/100\n", animal->happiness);
    printf("=================\n");
}

Animal** createZoo(int size) {
    Animal** zoo = malloc(size * sizeof(Animal*));
    if (!zoo) return NULL;

    for (int i = 0; i < size; i++) {
        zoo[i] = createRandomAnimal();
    }
    return zoo;
}

void feedAnimal(Animal* animal) {
    if (!animal) return;

    animal->hunger -= 20;
    if (animal->hunger < 0) animal->hunger = 0;
    animal->happiness += 10;
    if (animal->happiness > 100) animal->happiness = 100;

    printf("%s has been fed! Hunger decreased, happiness increased.\n", animal->name);
}

void playWithAnimal(Animal* animal) {
    if (!animal) return;

    animal->happiness += 15;
    if (animal->happiness > 100) animal->happiness = 100;
    animal->hunger += 5;
    if (animal->hunger > 100) animal->hunger = 100;

    printf("Played with %s! %s is happier but a bit hungrier.\n", animal->name, animal->name);
}

void printZoo(Animal** zoo, int size) {
    printf("\n========== Zoo Status ==========\n");
    printf("Total animals: %d\n", size);
    for (int i = 0; i < size; i++) {
        printf("%d. %s (%s)\n", i+1, zoo[i]->name, type_names[zoo[i]->type]);
    }
    printf("===============================\n");
}

void freeZoo(Animal** zoo, int size) {
    for (int i = 0; i < size; i++) {
        free(zoo[i]);
    }
    free(zoo);
}

int main() {
    srand(time(NULL));

    int zoo_size = 5;
    Animal** zoo = createZoo(zoo_size);
    if (!zoo) {
        printf("Failed to create zoo!\n");
        return 1;
    }

    printf("Welcome to Zoo Management Game!\n");
    printf("You have %d animals in your zoo.\n\n", zoo_size);

    int choice;
    while (1) {
        printf("\nChoose an action:\n");
        printf("1. View zoo status\n");
        printf("2. View animal details\n");
        printf("3. Feed an animal\n");
        printf("4. Play with an animal\n");
        printf("0. Exit\n");
        printf("Enter choice: ");

        scanf("%d", &choice);

        switch (choice) {
            case 1:
                printZoo(zoo, zoo_size);
                break;

            case 2: {
                int index;
                printf("Enter animal number (1-%d): ", zoo_size);
                scanf("%d", &index);
                if (index >= 1 && index <= zoo_size) {
                    printAnimal(zoo[index-1]);
                } else {
                    printf("Invalid animal number!\n");
                }
                break;
            }

            case 3: {
                int index;
                printf("Choose animal to feed (1-%d): ", zoo_size);
                scanf("%d", &index);
                if (index >= 1 && index <= zoo_size) {
                    feedAnimal(zoo[index-1]);
                } else {
                    printf("Invalid animal number!\n");
                }
                break;
            }

            case 4: {
                int index;
                printf("Choose animal to play with (1-%d): ", zoo_size);
                scanf("%d", &index);
                if (index >= 1 && index <= zoo_size) {
                    playWithAnimal(zoo[index-1]);
                } else {
                    printf("Invalid animal number!\n");
                }
                break;
            }

            case 0:
                printf("Thanks for playing Zoo Management Game!\n");
                freeZoo(zoo, zoo_size);
                return 0;

            default:
                printf("Invalid choice!\n");
        }
    }
}