#include <stdio.h>
#include <stdint.h>
#include <stdarg.h>
#include <stdlib.h>

enum type {
    INT = 0,
    FLOAT = 1,
    STRING = 2,
    BOOL = 3,
    LIST = 4,
    DICT = 5,
    TUPLE = 6,
    SET = 7,
    ANY = 8
};

typedef struct dynamic_type {
    uint8_t type;
    void* value;
} dynamic_t;

typedef struct dynamic_list {
    dynamic_t* value;
    int length;
    int capacity;
} dynamic_list_t;

dynamic_t* init_dynamic_var(uint8_t type, void* value) {
    // malloc the var
    dynamic_t* var = malloc(sizeof(dynamic_t));
    var->type = type;
    var->value = value;
    return var;
}

dynamic_t* init_dynamic_list(int num, ...) {
    // malloc the list
    dynamic_list_t* list = malloc(sizeof(dynamic_list_t));
    list->length = 0;
    list->capacity = num;
    list->value = malloc(num * sizeof(dynamic_t));

    // add the values to the list
    va_list valist;
    va_start(valist, num);

    for (int i = 0; i < num; i++) {
        dynamic_t* arg = va_arg(valist, dynamic_t*);
        list->value[i] = *arg;
        list->length++;
    }

    va_end(valist);

    // return the list
    dynamic_t* var = malloc(sizeof(dynamic_t));
    var->type = LIST;
    var->value = list;
    return var;
}

void dynamic_print(char end, int num, ...) {
    // act like python's print function
    va_list valist;
    va_start(valist, num);

    for (int i = 0; i < num; i++) {
        dynamic_t* arg = va_arg(valist, dynamic_t*);
        if (arg->type == INT) {
            printf("%d", (int*)arg->value);
        } else if (arg->type == FLOAT) {
            printf("%f", *(float*)arg->value);
        } else if (arg->type == STRING) {
            printf("%s", (char*)arg->value);
        } else if (arg->type == BOOL) {
            printf("%s", &arg->value ? "true" : "false");
        } else if (arg->type == LIST) {
            printf("[");

            dynamic_list_t* list = (dynamic_list_t*)arg->value;

            for (size_t i = 0; i < list->length; i++)
            {
                dynamic_print('\0', 1, list->value + i);
                if (i != list->length - 1) {
                    printf(", ");
                }
            }
            
            printf("]");
        }

        if (i != num - 1) {
            printf(" ");
        }
    }

    va_end(valist);
    printf("%c", end);
}

void append(dynamic_list_t* list, dynamic_t* value) {
    if (list->length == list->capacity) {
        list->capacity *= 2;
        dynamic_t* temp = list->value;
        list->value = malloc(list->capacity * sizeof(dynamic_t));
        for (size_t i = 0; i < list->length; i++) {
            list->value[i] = temp[i];
        }
    }

    list->value[list->length++] = *value;
}

int main(int argc, char *argv[]) {
    dynamic_t* a = init_dynamic_var(INT, (void*)1);
    dynamic_t* b = init_dynamic_var(FLOAT, (void*)&(float){1.5});
    dynamic_t* c = init_dynamic_var(STRING, (void*)"hello");
    dynamic_t* d = init_dynamic_list(3, a, b, c);

    dynamic_print('\n', 4, a, b, c, d);

    dynamic_t* e = init_dynamic_var(BOOL, (void*)1);
    dynamic_print('\n', 1, e);

    append(d->value, e);

    dynamic_print('\n', 1, d);
}