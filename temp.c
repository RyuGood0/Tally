dynamic_t* a = init_dynamic_var(INT, (void*)&(int){5});
char* b = "fstring("a is %s", (char* []){dynamic_var_to_string(a)})";
pprint(3, (char* []){copy_string("hello world"), dynamic_var_to_string(a), copy_string(b)})
