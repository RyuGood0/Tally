#ifndef BACKEND_H
#define BACKEND_H

#include <stdlib.h>
#include <string.h>
#include <stdint.h>

// Define the type for dynamic variables
typedef enum type { INT, FLOAT, STRING, LIST, DICT, BOOL, FREED } type_t;

// Define the structure for dynamic variables
typedef struct dynamic_type  {
    uint8_t type;
    void* value;
} dynamic_t;

// Define the structure for a dynamic list
typedef struct dynamic_list  {
    dynamic_t** value;
    int length;
    int capacity;
} dynamic_list_t;

// Define the structure for a dictionary
typedef struct dynamic_dict_pair  {
    int64_t key;
    dynamic_t* value;
} dynamic_dict_pair_t;

typedef struct dynamic_dict  {
    dynamic_dict_pair_t** pairs;
    int length;
    int capacity;
    int (*hash)(int64_t, int);
} dynamic_dict_t;

// Functions
dynamic_t* init_dynamic_var(type_t type, void* value);
void free_dynamic_var(dynamic_t** var);
void free_dynamic_list(dynamic_list_t* list);

dynamic_t* add_dynamic_vars(dynamic_t*, dynamic_t*);
dynamic_t* sub_dynamic_vars(dynamic_t*, dynamic_t*);
dynamic_t* mult_dynamic_vars(dynamic_t*, dynamic_t*);
dynamic_t* div_dynamic_vars(dynamic_t*, dynamic_t*);

char* dynamic_var_to_string(dynamic_t*);
char* copy_string(char*);
char* int_to_string(int);
char* float_to_string(float);
char* bool_to_string(int);

// Other functions
void pprint(int, ...);

#endif // BACKEND_H