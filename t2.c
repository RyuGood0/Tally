#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include "t2.h"

// Simple hash function
int dict_hash(int64_t key, int capacity) {
    return (int) (key % capacity);
}

// Initialize a new dictionary with initial capacity
dynamic_dict_t* init_dynamic_dict(int capacity) {
    dynamic_dict_t* dict = malloc(sizeof(dynamic_dict_t));
    dict->length = 0;
    dict->capacity = capacity;
    dict->pairs = malloc(capacity * sizeof(dynamic_dict_pair_t*));
    dict->hash = dict_hash;
    return dict;
}

// Resize the dictionary when it's full
void resize_dynamic_dict(dynamic_dict_t* dict) {
    int new_capacity = dict->capacity * 2;
    dynamic_dict_t* new_dict = init_dynamic_dict(new_capacity);
    for (int i = 0; i < dict->length; i++) {
        int index = new_dict->hash(dict->pairs[i]->key, new_capacity);
        if (new_dict->pairs[index] == NULL) {
            new_dict->pairs[index] = malloc(sizeof(dynamic_dict_pair_t));
        }
        new_dict->pairs[index]->key = dict->pairs[i]->key;
        new_dict->pairs[index]->value = dict->pairs[i]->value;
    }
    free(dict->pairs);
    free(dict);
    *dict = *new_dict;
}

// Add a key-value pair to the dictionary
void add_dynamic_dict_pair(dynamic_dict_t* dict, int64_t key, dynamic_t* value) {
    int index = dict->hash(key, dict->capacity);
    if (dict->pairs[index] == NULL) {
        dict->pairs[index] = malloc(sizeof(dynamic_dict_pair_t));
        dict->length++;
    }
    dict->pairs[index]->key = key;
    dict->pairs[index]->value = value;
    // Check if dictionary needs to be resized
    if (dict->length > 0.5 * dict->capacity) {
        resize_dynamic_dict(dict);
    }
}

// Get a value from the dictionary by key
dynamic_t* get_dynamic_dict_value(dynamic_dict_t* dict, int64_t key) {
    int index = dict->hash(key, dict->capacity);
    return dict->pairs[index]->value;
}

// Free the dictionary and its contents
void free_dynamic_dict(dynamic_dict_t* dict) {
    for (int i = 0; i < dict->capacity; i++) {
        if (dict->pairs[i] != NULL) {
            free_dynamic_var(&dict->pairs[i]->value);
            free(dict->pairs[i]);
        }
    }
    free(dict->pairs);
    free(dict);
}

// Initialize a dynamic variable
dynamic_t* init_dynamic_var(type_t type, void* value) {
    // malloc the var
    dynamic_t* var = malloc(sizeof(dynamic_t));
    var->type = type;
    if (type == STRING) {
        char* str = malloc(strlen((char*)value) + 1);
        strcpy(str, (char*)value);
        var->value = (void*)str;
    } else {
        var->value = value;
    }

    return var;
}

// Update the value of a dynamic variable
void update_dynamic_var(dynamic_t* var, type_t type, void* value) {
    if (var->type == STRING) {
        free((char*)var->value);
    } else if (var->type == LIST) {
        free_dynamic_list(var->value);
    } else if (var->type == DICT) {
        free_dynamic_dict(var->value);
    }
    var->type = type;
    var->value = value;
}

// Create a dynamic list
dynamic_list_t* init_dynamic_list(int num, ...) {
    va_list valist;
    va_start(valist, num);
    dynamic_list_t* list = malloc(sizeof(dynamic_list_t));
    list->length = num;
    list->capacity = num;
    list->value = malloc(num * sizeof(dynamic_t *));
    for (int i = 0; i < num; i++) {
        list->value[i] = va_arg(valist, dynamic_t *);
    }
    va_end(valist);
    return list;
}

dynamic_t* alloc_dynamic_list(int capacity) {
    dynamic_t* list = malloc(sizeof(dynamic_t));
    list->type = LIST;
    list->value = malloc(sizeof(dynamic_list_t));

    dynamic_list_t* list_value = (dynamic_list_t*)list->value;
    list_value->length = 0;
    list_value->capacity = capacity;
    list_value->value = malloc(capacity * sizeof(dynamic_t));

    return list;
}

void append_dynamic_list(dynamic_list_t* list, dynamic_t* value) {
    if (list->length == list->capacity) {
        list->capacity *= 2;
        dynamic_t** temp = list->value;
        list->value = malloc(list->capacity * sizeof(dynamic_t));
        for (size_t i = 0; i < list->length; i++) {
            list->value[i] = temp[i];
        }

        free(temp);
        temp = NULL;
    }

    list->value[list->length++] = value;
}

void free_dynamic_var(dynamic_t** var) {
    if ((*var)->type == FREED) {
        return;
    }
    if ((*var)->type == STRING) {
        free((*var)->value);
    } else if ((*var)->type == LIST) {
        free_dynamic_list((dynamic_list_t*)(*var)->value);
    }

    (*var)->value = NULL;
    (*var)->type = FREED;
    free(*var);
    *var = NULL;
}

// Free a dynamic list
void free_dynamic_list(dynamic_list_t* list) {
    for (size_t i = 0; i < list->length; i++) {
        free_dynamic_var(&list->value[i]);
    }

    free(list->value);
    free(list);
}

dynamic_t* add_dynamic_vars(dynamic_t* first, dynamic_t* second) {
    if (first->type == INT && second->type == INT) {
        int result = *(int*)first->value + *(int*)second->value;
        return init_dynamic_var(INT, (void*)&result);
    } else if (first->type == FLOAT && second->type == FLOAT) {
        float result = *(float*)first->value + *(float*)second->value;
        return init_dynamic_var(FLOAT, (void*)&result);
    } else if (first->type == STRING && second->type == STRING) {
        char* result = malloc(strlen((char*)first->value) + strlen((char*)second->value) + 1);
        strcpy(result, (char*)first->value);
        strcat(result, (char*)second->value);

        dynamic_t* new = init_dynamic_var(STRING, (void*) result);
        free(result);
        return new;
    } else if (first->type == LIST && second->type == LIST) {
        dynamic_list_t* first_list = (dynamic_list_t*)first->value;
        dynamic_list_t* second_list = (dynamic_list_t*)second->value;

        dynamic_t* list = alloc_dynamic_list(first_list->length + second_list->length);

        for (size_t i = 0; i < first_list->length; i++) {
            append_dynamic_list((dynamic_list_t*)list->value, first_list->value[i]);
        }

        for (size_t i = 0; i < second_list->length; i++) {
            append_dynamic_list((dynamic_list_t*)list->value, second_list->value[i]);
        }

        return list;
    } else if ((first->type == INT && second->type == FLOAT) || (first->type == FLOAT && second->type == INT)) {
        if (first->type == INT) {
            return init_dynamic_var(FLOAT, (void*)&(float){*(int*)first->value + *(float*)second->value});
        } else {
            return init_dynamic_var(FLOAT, (void*)&(float){*(float*)first->value + *(int*)second->value});
        }
    } else if ((first->type == INT && second->type == STRING) || (first->type == STRING && second->type == INT)) {
        char* result;
        if (first->type == INT) {
            size_t length = snprintf( NULL, 0, "%d", *(int*) first->value) + strlen((char*)second->value);

            result = malloc(length + 1);
            sprintf(result, "%d%s", *(int*)first->value, (char*)second->value);
        } else {
            size_t length = snprintf( NULL, 0, "%d", *(int*) second->value) + strlen((char*)first->value);

            result = malloc(length + 1);
            sprintf(result, "%s%d", (char*)first->value, *(int*)second->value);
        }

        dynamic_t* new = init_dynamic_var(STRING, (void*) result);
        free(result);
        return new;
    } else if ((first->type == INT && second->type == BOOL) || (first->type == BOOL && second->type == INT)) {
        int result = *(int*)first->value + *(int*)second->value;

        return init_dynamic_var(INT, (void*)&result);
    } else if ((first->type == FLOAT && second->type == STRING) || (first->type == STRING && second->type == FLOAT)) {
        char* result;
        if (first->type == FLOAT) {
            size_t length = snprintf( NULL, 0, "%f", *(float*) first->value) + strlen((char*)second->value);

            result = malloc(length + 1);
            sprintf(result, "%f%s", *(float*)first->value, (char*)second->value);
        } else {
            size_t length = snprintf( NULL, 0, "%f", *(float*) second->value) + strlen((char*)first->value);

            result = malloc(length + 1);
            sprintf(result, "%s%f", (char*)first->value, *(float*)second->value);
        }

        dynamic_t* new = init_dynamic_var(STRING, (void*) result);
        free(result);
        return new;
    } else if ((first->type == FLOAT && second->type == BOOL) || (first->type == BOOL && second->type == FLOAT)) {
        float result = *(float*)first->value + *(int*)second->value;

        return init_dynamic_var(FLOAT, (void*)&result);
    } else {
        return NULL;
    }
}

dynamic_t* sub_dynamic_vars(dynamic_t* first, dynamic_t* second) {
    if (first->type == INT && second->type == INT) {
        int result = *(int*)first->value - *(int*)second->value;
        return init_dynamic_var(INT, (void*)&result);
    } else if (first->type == FLOAT && second->type == FLOAT) {
        float result = *(float*)first->value - *(float*)second->value;
        return init_dynamic_var(FLOAT, (void*)&result);
    } else if ((first->type == INT && second->type == FLOAT) || (first->type == FLOAT && second->type == INT)) {
        if (first->type == INT) {
            return init_dynamic_var(FLOAT, (void*)&(float){*(int*)first->value - *(float*)second->value});
        } else {
            return init_dynamic_var(FLOAT, (void*)&(float){*(float*)first->value - *(int*)second->value});
        }
    } else if ((first->type == INT && second->type == STRING) || (first->type == STRING && second->type == INT)) {
        int result;
        if (first->type == INT) {
            result = atoi((char*)second->value);
            if (result == 0 && ((char*)second->value)[0] != '0') {
                return NULL;
            }

            result = *(int*)first->value - result;
        } else {
            result = atoi((char*)first->value);
            if (result == 0 && ((char*)first->value)[0] != '0') {
                return NULL;
            }

            result = result - *(int*)second->value;
        }

        return init_dynamic_var(INT, (void*)&result);
    } else if ((first->type == INT && second->type == BOOL) || (first->type == BOOL && second->type == INT)) {
        int result = *(int*)first->value - *(int*)second->value;
        return init_dynamic_var(INT, (void*)&result);
    } else if ((first->type == FLOAT && second->type == STRING) || (first->type == STRING && second->type == FLOAT)) {
        float result;
        if (first->type == FLOAT) {
            result = atof((char*)second->value);
            if (result == 0 && ((char*)second->value)[0] != '0') {
                return NULL;
            }

            result = *(float*)first->value - result;
        } else {
            result = atof((char*)first->value);
            if (result == 0 && ((char*)first->value)[0] != '0') {
                return NULL;
            }

            result = result - *(float*)second->value;
        }

        return init_dynamic_var(FLOAT, (void*)&result);
    } else if ((first->type == FLOAT && second->type == BOOL) || (first->type == BOOL && second->type == FLOAT)) {
        float result = *(int*)first->value - *(float*)second->value;

        return init_dynamic_var(FLOAT, (void*)&result);
    } else {
        return NULL;
    }
}

dynamic_t* mult_dynamic_vars(dynamic_t* first, dynamic_t* second) {
    if (first->type == INT && second->type == INT) {
        int result = *(int*)first->value * *(int*)second->value;
        return init_dynamic_var(INT, (void*)&result);
    } else if (first->type == FLOAT && second->type == FLOAT) {
        float result = *(float*)first->value * *(float*)second->value;
        return init_dynamic_var(FLOAT, (void*)&result);
    } else if ((first->type == INT && second->type == FLOAT) || (first->type == FLOAT && second->type == INT)) {
        if (first->type == INT) {
            return init_dynamic_var(FLOAT, (void*)&(float){*(int*)first->value * *(float*)second->value});
        } else {
            return init_dynamic_var(FLOAT, (void*)&(float){*(float*)first->value * *(int*)second->value});
        }
    } else if ((first->type == INT && second->type == STRING) || (first->type == STRING && second->type == INT)) {
        char* result;
        if (first->type == INT) {
            result = (char*) malloc(strlen((char*)second->value) * *(int*)first->value + 1);
            strcpy(result, (char*)first->value);
            for (size_t i = 0; i < *(int*)first->value; i++) {
                strcat(result, (char*)second->value);
            }
        } else {
            result = (char*) malloc(strlen((char*)first->value) * *(int*)second->value + 1);
            strcpy(result, (char*)second->value);
            for (size_t i = 0; i < *(int*)second->value; i++) {
                strcat(result, (char*)first->value);
            }
        }

        dynamic_t* new = init_dynamic_var(STRING, (void*) result);
        free(result);
        return new;
    } else if ((first->type == INT && second->type == BOOL) || (first->type == BOOL && second->type == INT)) {
        int result = *(int*)first->value * *(int*)second->value;

        return init_dynamic_var(INT, (void*)&result);
    } else if ((first->type == FLOAT && second->type == BOOL) || (first->type == BOOL && second->type == FLOAT)) {
        float result = *(float*)first->value * *(int*)second->value;

        return init_dynamic_var(FLOAT, (void*)&result);
    } else {
        return NULL;
    }
}

dynamic_t* div_dynamic_vars(dynamic_t* first, dynamic_t* second) {
if (first->type == INT && second->type == INT) {
        int result = (float) *(int*)first->value / *(int*)second->value;
        return init_dynamic_var(FLOAT, (void*)&result);
    } else if (first->type == FLOAT && second->type == FLOAT) {
        float result = *(float*)first->value / *(float*)second->value;
        return init_dynamic_var(FLOAT, (void*)&result);
    } else if ((first->type == INT && second->type == FLOAT) || (first->type == FLOAT && second->type == INT)) {
        if (first->type == INT) {
            return init_dynamic_var(FLOAT, (void*)&(float){*(int*)first->value / *(float*)second->value});
        } else {
            return init_dynamic_var(FLOAT, (void*)&(float){*(float*)first->value / *(int*)second->value});
        }
    } else {
        return NULL;
    }
}

// Create a string from an integer
char* int_to_string(int val) {
    size_t length = snprintf(NULL, 0, "%d", val);
    char* result = malloc(length + 1);
    sprintf(result, "%d", val);
    return result;
}

// Create a string from a float
char* float_to_string(float val) {
    size_t length = snprintf(NULL, 0, "%f", val);
    char* result = malloc(length + 1);
    sprintf(result, "%f", val);
    return result;
}

// Create a string from a boolean
char* bool_to_string(int val) {
    char* result; 
    if(val==0){ 
        result=malloc(6); 
        strcpy(result, "False"); 
     } else { 
        result=malloc(5); 
        strcpy(result, "True"); 
     }

    return result;
}

// Create a string from a dynamic variable
char* dynamic_var_to_string(dynamic_t* var) {
    if(var->type==STRING){ 
        char* result=malloc(strlen((char*)var->value)+1); 
        strcpy(result,(char*)var->value); 

        return result; 
    } else if(var->type==INT){ 
        size_t length=strlen(int_to_string(*(int*)var->value)); 
        char* result=malloc(length+1); 
        sprintf(result,"%d",*(int*)var->value); 

        return result; 
    } else if(var->type==FLOAT){ 
        size_t length=strlen(float_to_string(*(float*)var->value)); 
        char* result=malloc(length+1); 
        sprintf(result,"%f",*(float*)var->value); 

        return result; 
    } else if(var->type==BOOL){ 
        char* result=bool_to_string(*(int*)var->value); 

        return result; 
    } else if(var->type==LIST){ 
        dynamic_list_t* list=(dynamic_list_t*)var->value; 
        char**temp=malloc(list->length*sizeof(char*)); 
        size_t length=0; 

        for(size_t i=0;i<list->length;i++){ 
            temp[i]=dynamic_var_to_string(list->value[i]); 
            length+=strlen(temp[i]); 
         } 

        char*result=calloc(length+list->length*2+1,sizeof(char)); 
        result[0]='['; 

        for(size_t i=0;i<list->length;i++){ 
            strcat(result,temp[i]); 
            if(i!=list->length-1){ 
                strcat(result,", "); 
             } 
         } 

        result[length+list->length*2-1]=']'; 

        //free the temp
        for(size_t i=0;i<list->length;i++){ 
            free(temp[i]); 
        } 
        free(temp); 

        return result; 
    } else { 
        return NULL; 
    }
}

#include <stdio.h>
int main() {
    // Create dynamic variables
    dynamic_t* int_var = init_dynamic_var(INT, (void*)&(int){3});

    dynamic_t* float_var = init_dynamic_var(FLOAT, (void*)&(float){1.5});

    dynamic_t* string_var = init_dynamic_var(STRING, (void*)"hello");

    dynamic_t* bool_var = init_dynamic_var(BOOL, (void*)&(int){1});

    // Test addition
    dynamic_t* add_result = add_dynamic_vars(int_var, float_var);
    if (add_result != NULL) {
        printf("Addition: %s\n", dynamic_var_to_string(add_result));
    }

    // Test subtraction
    dynamic_t* sub_result = sub_dynamic_vars(int_var, bool_var);
    if (sub_result != NULL) {
        printf("Subtraction: %s\n", dynamic_var_to_string(sub_result));
    }

    // Test multiplication
    dynamic_t* mult_result = mult_dynamic_vars(float_var, string_var);
    if (mult_result != NULL) {
        printf("Multiplication: %s\n", dynamic_var_to_string(mult_result));
    }

    // Test division
    dynamic_t* div_result = div_dynamic_vars(int_var, bool_var);
    if (div_result != NULL) {
        printf("Division: %s\n", dynamic_var_to_string(div_result));
    }

    // Free dynamic variables
    free_dynamic_var(&int_var);
    free_dynamic_var(&float_var);
    free_dynamic_var(&string_var);
    free_dynamic_var(&bool_var);

    return 0;
}