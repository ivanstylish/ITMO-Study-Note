#include <stdlib.h>
#include <stdio.h>
#include <memory.h>
 
typedef struct {
    int x;
    int y;
} Point;
 
typedef enum {
    WARRIOR,
    ARCHER,
    MAGE
} UNIT_TYPES;
 
typedef struct {
    char* name;
    int health;
    int maxHealth;
    int damage;
    UNIT_TYPES type;
    Point position;
} Unit;
 
Unit* createUnit(char* name, int health, int damage, UNIT_TYPES type, Point position) {
    Unit* unit = (Unit*)malloc(sizeof(Unit));
 
    if (!unit) {
        fprintf(stderr, "Memory allocation failed\n");
        return NULL;
    }
 
    unit->name = name;
    unit->health = health;
    unit->maxHealth = health;
    unit->damage = damage;
    unit->type = type;
    unit->position = position;
 
    return unit;
}
 
Point* createRandomPoint() {
    Point* point = (Point*)malloc(sizeof(Point));
 
    if (!point) {
        fprintf(stderr, "Memory allocation failed\n");
        return NULL;
    }
 
    point->x = rand() % 100;
    point->y = rand() % 100;
 
    return point;
}
 
Unit** createArmy(int size) {
    Unit** army = (Unit**)malloc(size * sizeof(Unit*));
 
    if (!army) {
        fprintf(stderr, "Memory allocation failed\n");
        return NULL;
    }
 
    for (int i = 0; i < size; i++) {
        Point* position = createRandomPoint();
        army[i] = createUnit("Soldier", 100, 10, WARRIOR, *position);
        free(position);
    }
 
    return army;
}
 
void printUnit(const Unit* unit) {
    if (!unit) {
        fprintf(stderr, "Invalid unit\n");
        return;
    }
 
    const char* typeStr;
    switch (unit->type) {
    case WARRIOR:
        typeStr = "Warrior";
        break;
    case ARCHER:
        typeStr = "Archer";
        break;
    case MAGE:
        typeStr = "Mage";
        break;
    default:
        typeStr = "Unknown";
        break;
    }
 
    printf("Name: %s\n", unit->name);
    printf("Health: %d/%d\n", unit->health, unit->maxHealth);
    printf("Damage: %d\n", unit->damage);
    printf("Type: %s\n", typeStr);
    printf("Position: (%d, %d)\n", unit->position.x, unit->position.y);
}
 
void serializeUnit(const Unit* unit, const char* filename) {
    if (!unit || !filename) {
        fprintf(stderr, "Invalid arguments for serialization\n");
        return;
    }
 
    FILE* file = fopen(filename, "wb");
    if (!file) {
        fprintf(stderr, "Failed to open file for writing\n");
        return;
    }
 
    fwrite(unit, sizeof(Unit), 1, file);
    fclose(file);
}
 
Unit* deserializeUnit(const char* filename) {
    if (!filename) {
        fprintf(stderr, "Invalid filename for deserialization\n");
        return NULL;
    }
 
    FILE* file = fopen(filename, "rb");
    if (!file) {
        fprintf(stderr, "Failed to open file for reading\n");
        return NULL;
    }
 
    Unit* unit = (Unit*)malloc(sizeof(Unit));
    if (!unit) {
        fprintf(stderr, "Memory allocation failed\n");
        fclose(file);
        return NULL;
    }
 
    fread(unit, sizeof(Unit), 1, file);
    fclose(file);
 
    return unit;
}
 
 
int main() {
    Unit* unit = createUnit("Hero", 150, 25, MAGE, (Point) { 10, 20 });
    if (!unit) {
        return -1;
    }
    printUnit(unit);
    serializeUnit(unit, "unit.dat");
    free(unit);
    Unit* loadedUnit = deserializeUnit("unit.dat");
    if (loadedUnit) {
        printUnit(loadedUnit);
        free(loadedUnit);
    }
 
 
    return 0;
}