#include <stdlib.h>
#include <stdio.h>
#include <memory.h>
#include <string.h>
#include <time.h>

typedef struct {
    int x;
    int y;
} Position;

typedef enum {
    MAMMAL,
    BIRD,
    REPTILE,
    FISH
} ANIMAL_TYPES;

typedef enum {
    MALE,
    FEMALE,
    UNKNOWN
} SEX;

typedef struct {
    char* name;
    int age;
    double height;
    double weight;
    SEX sex;
    ANIMAL_TYPES type;
    Position position;
    int hunger;
    int happiness;
} Animal;

Animal* createAnimal(char* name, int age, double height, double weight, SEX sex, ANIMAL_TYPES type, Position position) {
    Animal* animal = (Animal*)malloc(sizeof(Animal));

    if (!animal) {
        fprintf(stderr, "Memory allocation failed\n");
        return NULL;
    }

    animal->name = name;
    animal->age = age;
    animal->height = height;
    animal->weight = weight;
    animal->sex = sex;
    animal->type = type;
    animal->position = position;
    animal->hunger = 50 + rand() % 30;
    animal->happiness = 60 + rand() % 30;

    return animal;
}

Position* createRandomPosition() {
    Position* position = (Position*)malloc(sizeof(Position));

    if (!position) {
        fprintf(stderr, "Memory allocation failed\n");
        return NULL;
    }

    position->x = rand() % 100;
    position->y = rand() % 100;

    return position;
}

Animal** createZoo(int size) {
    Animal** zoo = (Animal**)malloc(size * sizeof(Animal*));

    if (!zoo) {
        fprintf(stderr, "Memory allocation failed\n");
        return NULL;
    }

    char* names[] = { "Leo", "Bella", "Max", "Luna", "Charlie" };

    for (int i = 0; i < size; i++) {
        Position* position = createRandomPosition();
        zoo[i] = createAnimal(names[i % 5], 2 + rand() % 10, 1.0 + (rand() % 200) / 100.0,
            20.0 + (rand() % 100) / 10.0, rand() % 3, rand() % 4, *position);
        free(position);
    }

    return zoo;
}

void printAnimal(const Animal* animal) {
    if (!animal) {
        fprintf(stderr, "Invalid animal\n");
        return;
    }

    const char* typeStr;
    switch (animal->type) {
    case MAMMAL:
        typeStr = "Mammal";
        break;
    case BIRD:
        typeStr = "Bird";
        break;
    case REPTILE:
        typeStr = "Reptile";
        break;
    case FISH:
        typeStr = "Fish";
        break;
    default:
        typeStr = "Unknown";
        break;
    }

    const char* sexStr;
    switch (animal->sex) {
    case MALE:
        sexStr = "Male";
        break;
    case FEMALE:
        sexStr = "Female";
        break;
    case UNKNOWN:
        sexStr = "Unknown";
        break;
    default:
        sexStr = "Unknown";
        break;
    }

    printf("Name: %s\n", animal->name);
    printf("Age: %d years\n", animal->age);
    printf("Height: %.2f m\n", animal->height);
    printf("Weight: %.2f kg\n", animal->weight);
    printf("Type: %s\n", typeStr);
    printf("Sex: %s\n", sexStr);
    printf("Position: (%d, %d)\n", animal->position.x, animal->position.y);
    printf("Hunger: %d/100\n", animal->hunger);
    printf("Happiness: %d/100\n", animal->happiness);
    printf("--------------------\n");
}

void feedAnimal(Animal* animal) {
    if (!animal) return;

    animal->hunger -= 20;
    if (animal->hunger < 0) animal->hunger = 0;
    animal->happiness += 10;
    if (animal->happiness > 100) animal->happiness = 100;

    printf("%s has been fed!\n", animal->name);
}

void playWithAnimal(Animal* animal) {
    if (!animal) return;

    animal->happiness += 15;
    if (animal->happiness > 100) animal->happiness = 100;
    animal->hunger += 5;
    if (animal->hunger > 100) animal->hunger = 100;

    printf("Played with %s!\n", animal->name);
}

void serializeAnimal(const Animal* animal, const char* filename) {
    if (!animal || !filename) {
        fprintf(stderr, "Invalid arguments for serialization\n");
        return;
    }

    FILE* file = fopen(filename, "wb");
    if (!file) {
        fprintf(stderr, "Failed to open file for writing\n");
        return;
    }

    fwrite(animal, sizeof(Animal), 1, file);
    fclose(file);
}

Animal* deserializeAnimal(const char* filename) {
    if (!filename) {
        fprintf(stderr, "Invalid filename for deserialization\n");
        return NULL;
    }

    FILE* file = fopen(filename, "rb");
    if (!file) {
        fprintf(stderr, "Failed to open file for reading\n");
        return NULL;
    }

    Animal* animal = (Animal*)malloc(sizeof(Animal));
    if (!animal) {
        fprintf(stderr, "Memory allocation failed\n");
        fclose(file);
        return NULL;
    }

    fread(animal, sizeof(Animal), 1, file);
    fclose(file);

    return animal;
}

int main() {
    srand(time(NULL));

    Animal* lion = createAnimal("King Lion", 5, 1.2, 180.5, MALE, MAMMAL, (Position) { 15, 25 });
    if (!lion) {
        return -1;
    }

    printf("=== Original Animal ===\n");
    printAnimal(lion);
    feedAnimal(lion);
    playWithAnimal(lion);

    printf("\n=== After Feeding and Playing ===\n");
    printAnimal(lion);

    serializeAnimal(lion, "animal.dat");
    free(lion);

    Animal* loadedAnimal = deserializeAnimal("animal.dat");
    if (loadedAnimal) {
        printf("\n=== Loaded Animal from File ===\n");
        printAnimal(loadedAnimal);
        free(loadedAnimal);
    }

    printf("\n=== Zoo Animals ===\n");
    int zoo_size = 3;
    Animal** zoo = createZoo(zoo_size);
    if (zoo) {
        for (int i = 0; i < zoo_size; i++) {
            printf("Animal %d:\n", i + 1);
            printAnimal(zoo[i]);
            free(zoo[i]);
        }
        free(zoo);
    }

    return 0;
}