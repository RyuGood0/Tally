#include <stdio.h>
#include <stdint.h>
#include <stdarg.h>

typedef struct dynamic_type {
    uint8_t type; // 0 = int, 1 = float, 2 = string, 3 = list, 4 = dict, 5 = tuple, 6 = set, 7 = bool, 8 = null, 9 = any
    void* value;
} dynamic_t;

void dynamic_print(char end, int num, ...) {
    // act like python's print function
    va_list valist;
    va_start(valist, num);

    for (int i = 0; i < num; i++) {
        dynamic_t* arg = va_arg(valist, dynamic_t*);
        if (arg->type == 0) {
            // printf("%d", *(int*)arg->value); -> Segmentation fault
            printf("%d", (int*)arg->value);
        } else if (arg->type == 1) {
            printf("%f", *(float*)arg->value);
        } else if (arg->type == 2) {
            printf("%s", (char*)arg->value);
        } else if (arg->type == 3) {
            printf("[");
            dynamic_print('\0', 3, &((dynamic_t*)arg->value)[0], &((dynamic_t*)arg->value)[1], &((dynamic_t*)arg->value)[2]);
            printf("]");
        }

        if (i != num - 1) {
            printf(" ");
        }
    }

    va_end(valist);
    printf("%c", end);
}

int main(int argc, char *argv[]) {
    dynamic_t a = {.type = 0, .value = (void*)1};
    dynamic_t b = {.type = 1, .value = (void*)&(float){1.5}};
    dynamic_t c = {.type = 2, .value = (void*)"hello"};
    dynamic_t d = {.type = 3, .value = (void*)&(dynamic_t[]){a, b, c}};
    
    dynamic_print('\n', 4, &a, &b, &c, &d);
}