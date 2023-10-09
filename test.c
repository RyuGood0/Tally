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

dynamic_t* update_dynamic_var(dynamic_t* var, int type, void* value) {
    if (var->type == STRING) {
        free(var->value);
    } else if (var->type == LIST) {
        free_dynamic_list((dynamic_list_t*)var->value);
    }

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

char* dynamic_var_to_string(dynamic_t* var) {
    if (var->type == STRING) {
        char* result = malloc(strlen((char*)var->value) + 1);
        strcpy(result, (char*)var->value);

        return result;
    } else if (var->type == INT) {
        size_t length = snprintf( NULL, 0, "%d", *(int*) var->value);

        char* result = malloc(length + 1);
        sprintf(result, "%d", *(int*)var->value);

        return result;
    } else if (var->type == FLOAT) {
        size_t length = snprintf( NULL, 0, "%f", *(float*) var->value);
            
        char* result = malloc(length + 1);
        sprintf(result, "%f", *(float*)var->value);

        return result;
    } else if (var->type == BOOL) {
        char* result;
        if (*(int*)var->value == 0) {
            result = malloc(6);
            strcpy(result, "False");
        } else {
            result = malloc(5);
            strcpy(result, "True");
        }

        return result;
    } else if (var->type == LIST) {
        dynamic_list_t* list = (dynamic_list_t*)var->value;

        char** temp = malloc(list->length * sizeof(char*));
        size_t length = 0;

        for (size_t i = 0; i < list->length; i++)
        {
            temp[i] = dynamic_var_to_string(list->value[i]);
            length += strlen(temp[i]);
        }

        char* result = calloc(length + list->length * 2 + 1, sizeof(char));
        result[0] = '[';
        
        for (size_t i = 0; i < list->length; i++)
        {
            strcat(result, temp[i]);
            if (i != list->length - 1) {
                strcat(result, ", ");
            }
        }

        result[length + list->length * 2 - 1] = ']';

        // free the temp
        for (size_t i = 0; i < list->length; i++)
        {
            free(temp[i]);
        }
        free(temp);

        return result;
    } else {
        return NULL;
    }
}

void print_dynamics(char end, int num, ...) {
    va_list valist;
    va_start(valist, num);

    for (int i = 0; i < num; i++) {
        dynamic_t* arg = va_arg(valist, dynamic_t*);
        char* str = dynamic_var_to_string(arg);
        printf("%s", str);
        free(str);

        if (i != num - 1) {
            printf(" ");
        }
    }

    va_end(valist);
    printf("%c", end);
}

char* fstring(char* format, char** args) {
    // act like python's fstring, all args are strings
    
    size_t length = 0;
    int found = 0;

    for (size_t i = 0; i < strlen(format); i++) {
        if (format[i] == '%') {
            if (format[i + 1] == 's') {
                length += strlen(args[found]);
                found++;
            } else {
                length += 2;
            }
        } else {
            length++;
        }
    }

    char* result = calloc(length + 1, sizeof(char));

    size_t index = 0;
    found = 0;

    for (size_t i = 0; i < strlen(format); i++) {
        if (format[i] == '%') {
            if (format[i + 1] == 's') {
                strcat(result, args[found]);
                found++;
                index++;
                i++;
            } else {
                result[index++] = format[i];
                result[index++] = format[i + 1];
                i++;
            }
        } else {
            result[index++] = format[i];
        }
    }

    // free the args
    for (size_t i = 0; i < found; i++) {
        free(args[i]);
    }
    
    return result;
}

void pprint(int length, char** args) {
    // act like python's print
    for (size_t i = 0; i < length; i++) {
        printf("%s", args[i]);
        free(args[i]);

        if (i != length - 1) {
            printf(" ");
        }
    }
    
    printf("\n");
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

char* copy_string(char* str) {
    char* result = malloc(strlen(str) + 1);
    strcpy(result, str);

    return result;
}

char* int_to_string(int val) {
    size_t length = snprintf( NULL, 0, "%d", val);

    char* result = malloc(length + 1);
    sprintf(result, "%d", val);

    return result;
}

char* float_to_string(float val) {
    size_t length = snprintf( NULL, 0, "%f", val);

    char* result = malloc(length + 1);
    sprintf(result, "%f", val);

    return result;
}

char* bool_to_string(int val) {
    char* result;
    if (val == 0) {
        result = malloc(6);
        strcpy(result, "False");
    } else {
        result = malloc(5);
        strcpy(result, "True");
    }

    return result;
}

int equals_int_string(int first, char* second) {
    int result = atoi(second);
    if (result == 0 && second[0] != '0') {
        return 0;
    }

    return first == result;
}

int equals_float_string(float first, char* second) {
    float result = atof(second);
    if (result == 0 && second[0] != '0') {
        return 0;
    }

    return first == result;
}

int dynamic_equals(dynamic_t* first, dynamic_t* second) {
    if (first->type == second->type) {
        if (first->type == INT) {
            return *(int*)first->value == *(int*)second->value;
        } else if (first->type == FLOAT) {
            return *(float*)first->value == *(float*)second->value;
        } else if (first->type == STRING) {
            return strcmp((char*)first->value, (char*)second->value) == 0;
        } else if (first->type == BOOL) {
            return *(int*)first->value == *(int*)second->value;
        } else if (first->type == LIST) {
            dynamic_list_t* first_list = (dynamic_list_t*)first->value;
            dynamic_list_t* second_list = (dynamic_list_t*)second->value;

            if (first_list->length != second_list->length) {
                return 0;
            }

            for (size_t i = 0; i < first_list->length; i++) {
                if (!dynamic_equals(first_list->value[i], second_list->value[i])) {
                    return 0;
                }
            }

            return 1;
        } else {
            return 0;
        }
    } else {
        if ((first->type == INT && second->type == FLOAT) || (first->type == FLOAT && second->type == INT)) {
            return *(int*)first->value == *(float*)second->value;
        } else if ((first->type == INT && second->type == BOOL) || (first->type == BOOL && second->type == INT)) {
            return *(int*)first->value == *(int*)second->value;
        } else if ((first->type == INT && second->type == STRING) || (first->type == STRING && second->type == INT)) {
            if (first->type == INT) {
                return equals_int_string(*(int*)first->value, (char*)second->value);
            } else {
                return equals_int_string(*(int*)second->value, (char*)first->value);
            }
        } else if ((first->type == FLOAT && second->type == STRING) || (first->type == STRING && second->type == FLOAT)) {
            if (first->type == INT) {
                return equals_float_string(*(float*)first->value, (char*)second->value);
            } else {
                return equals_float_string(*(float*)second->value, (char*)first->value);
            }
        }
        else {
            return 0;
        }
    }
}

int dynamic_not_equals(dynamic_t* first, dynamic_t* second) {
    return !dynamic_equals(first, second);
}

int dynamic_greater_than(dynamic_t* first, dynamic_t* second) {
    if (first->type == second->type) {
        if (first->type == INT) {
            return *(int*)first->value > *(int*)second->value;
        } else if (first->type == FLOAT) {
            return *(float*)first->value > *(float*)second->value;
        } else if (first->type == STRING) {
            return strcmp((char*)first->value, (char*)second->value) > 0;
        } else if (first->type == BOOL) {
            return *(int*)first->value > *(int*)second->value; 
        } else {
            return 0;
        }
    } else {
        if ((first->type == INT && second->type == FLOAT) || (first->type == FLOAT && second->type == INT)) {
            if (first->type == INT) {
                return *(int*)first->value > *(float*)second->value;
            } else {
                return *(float*)first->value > *(int*)second->value;
            }
        } else if ((first->type == INT && second->type == BOOL) || (first->type == BOOL && second->type == INT)) {
            return *(int*)first->value > *(int*)second->value;
        } else if ((first->type == FLOAT && second->type == BOOL) || (first->type == BOOL && second->type == FLOAT))
        {
            if (first->type == FLOAT) {
                return *(float*)first->value > *(int*)second->value;
            } else {
                return *(int*)first->value > *(float*)second->value;
            }
        }
        else {
            return 0;
        }
    }
}

int dynamic_greater_equals(dynamic_t* first, dynamic_t* second) {
    return dynamic_greater_than(first, second) || dynamic_equals(first, second);
}

int main(int argc, char *argv[]) {
    // dynamic vars
    dynamic_t* a = init_dynamic_var(INT, (void*)&(int){3});
    dynamic_t* b = init_dynamic_var(FLOAT, (void*)&(float){1.5});
    dynamic_t* c = init_dynamic_var(STRING, (void*)"hello");
    dynamic_t* d = init_dynamic_list(3, a, b, c);

    print_dynamics('\n', 4, a, b, c, d);

    // print(f"Hello {a}!")
    char* str_UUID = fstring("Hello %s! %s", (char* []){dynamic_var_to_string(a), copy_string("Hi")});
    dynamic_t* e = init_dynamic_var(STRING, (void*) str_UUID);
    free(str_UUID);
    pprint(2, (char* []){hello(), dynamic_var_to_string(e)});

    // if condition
    if (dynamic_equals(a, c)) {
        printf("a equals c\n");
    } else {
        printf("a not equals c\n");
    }

    // Free the allocated memory
    free_dynamic_var(&d);
    free_dynamic_var(&e);

    return 0;
}