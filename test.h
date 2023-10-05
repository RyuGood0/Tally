#include <stdint.h>
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
    ANY = 8,
    FREED = 255
};

typedef struct dynamic_type {
    uint8_t type;
    void* value;
} dynamic_t;

typedef struct dynamic_list {
    dynamic_t** value;
    int length;
    int capacity;
} dynamic_list_t;

dynamic_t* init_dynamic_var(uint8_t type, void* value);

dynamic_t* init_dynamic_list(int num, ...);

dynamic_t* alloc_dynamic_list(int capacity);

char* dynamic_var_to_string(dynamic_t* var);

void print_dynamics(char end, int num, ...);

char* fstring(char* format, char** args);

void pprint(int length, char** args);

void append(dynamic_list_t* list, dynamic_t* value);

void free_dynamic_list(dynamic_list_t* list);

void free_dynamic_var(dynamic_t** var);

dynamic_t* add_dynamic_vars(dynamic_t* first, dynamic_t* second);

dynamic_t* sub_dynamic_vars(dynamic_t* first, dynamic_t* second);

dynamic_t* mul_dynamic_vars(dynamic_t* first, dynamic_t* second);

dynamic_t* div_dynamic_vars(dynamic_t* first, dynamic_t* second);

char* copy_string(char* str);