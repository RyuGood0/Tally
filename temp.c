dynamic_t* a = init_dynamic_var(INT, (void*)&(int){5});
char* str_UUID_982c978458fb4df2a7916eae500222f8 = fstring("a is %s", (char* []){dynamic_var_to_string(a)});
dynamic_t* b = init_dynamic_var(STRING, (void*)str_UUID_982c978458fb4df2a7916eae500222f8);
free(str_UUID_982c978458fb4df2a7916eae500222f8);
pprint(3, (char* []){"hello world", dynamic_var_to_string(a), dynamic_var_to_string(b)})
char* str_UUID_751af0fadce240af876d057141a78aee = fstring("hello world %s %s", (char* []){dynamic_var_to_string(a), dynamic_var_to_string(b)});
pprint(1, (char* []){copy_string(str_UUID_751af0fadce240af876d057141a78aee);})
free(str_UUID_751af0fadce240af876d057141a78aee);
free_dynamic_var(a);
