#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>

#include "test.h"

dynamic_t* init_dynamic_var(uint8_t type, void* value) {
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

dynamic_t* init_dynamic_list(int num, ...) {
    // malloc the list
    dynamic_t* list = malloc(sizeof(dynamic_t));
    list->type = LIST;
    list->value = malloc(sizeof(dynamic_list_t));

    dynamic_list_t* list_value = (dynamic_list_t*)list->value;
    list_value->length = num;
    list_value->capacity = num;
    list_value->value = malloc(num * sizeof(dynamic_t));

    va_list valist;
    va_start(valist, num);

    for (int i = 0; i < num; i++) {
        dynamic_t* arg = va_arg(valist, dynamic_t*);
        list_value->value[i] = arg;
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

void dynamic_print(char end, int num, ...) {
    // act like python's print function
    va_list valist;
    va_start(valist, num);

    for (int i = 0; i < num; i++) {
        dynamic_t* arg = va_arg(valist, dynamic_t*);
        if (arg->type == INT) {
            printf("%d", *(int*)arg->value);
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
                dynamic_print('\0', 1, list->value[i]);
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

void free_dynamic_list(dynamic_list_t* list) {
    for (size_t i = 0; i < list->length; i++) {
        free_dynamic_var(&list->value[i]);
    }

    free(list->value);
    free(list);
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
            append((dynamic_list_t*)list->value, first_list->value[i]);
        }

        for (size_t i = 0; i < second_list->length; i++) {
            append((dynamic_list_t*)list->value, second_list->value[i]);
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
        int result = 0;
        if (first->type == INT) {
            result = *(int*)first->value + 1;
        } else {
            result = *(int*)second->value + 1;
        }

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
        float result = 0;
        if (first->type == FLOAT) {
            result = *(float*)first->value + 1;
        } else {
            result = *(float*)second->value + 1;
        }

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
        int result = 0;
        if (first->type == INT) {
            result = *(int*)first->value - 1;
        } else {
            result = 1 - *(int*)second->value;
        }

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
        float result = 0;
        if (first->type == FLOAT) {
            result = *(float*)first->value - 1;
        } else {
            result = 1 - *(float*)second->value;
        }

        return init_dynamic_var(FLOAT, (void*)&result);
    } else {
        return NULL;
    }
}

int main(int argc, char *argv[]) {
    dynamic_t* a = init_dynamic_var(INT, (void*)&(int){1});
    dynamic_t* b = init_dynamic_var(FLOAT, (void*)&(float){1.5});
    dynamic_t* c = init_dynamic_var(STRING, (void*)"1");
    dynamic_t* d = init_dynamic_list(3, a, b, c);

    dynamic_print('\n', 4, a, b, c, d);

    dynamic_t* e = init_dynamic_var(BOOL, (void*)1);
    dynamic_print('\n', 1, e);

    append(d->value, e);
    append(d->value, init_dynamic_var(STRING, (void*)"!"));

    dynamic_print('\n', 1, d);

    dynamic_t* f = init_dynamic_var(STRING, (void*)"world");

    dynamic_t* g = sub_dynamic_vars(e, b);
    dynamic_print('\n', 1, g);

    // Free the allocated memory
    free_dynamic_var(&d);
    free_dynamic_var(&f);
    free_dynamic_var(&g);

    return 0;
}