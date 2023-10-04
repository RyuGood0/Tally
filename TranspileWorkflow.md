# Vars

[type] var = [statement] => direct transpilation
var = [statement] => dynamic type transpilation

add to dictionnary with {name: [VariableObject]}

# Conditions and loops

if [condition] {
    [body]
}

=> transpile if statement then treat body like new block

while [condition] {
    [body]
}

=> transpile while statement then treat body like new block

for [var] in [iterable] {
    [body]
}

=> get iterable length and convert to for(int i = 0; i < length; i++) then treat body like new block

# Functions

[type] func [name]([typed args]) {
    [body]
}

=> transpiled directly as function then treat body like new block

func [name]([typed args]) {
    [body]
}

=> transpiled as dynamic type function then treat body like new block

func [name]([args]) {
    [body]
}

=> transpiled as dynamic type function with dynamic type args then treat body like new block

=> Create .h file with function prototypes and import it in main.c

# Fstring

f"STR AND {VAR_NAMES}"

```
// print(f"Hello {a}!")
char* args_UUID[2] = {dynamic_var_to_string(a), dynamic_var_to_string(b)};
char* str_UUID = fstring("Hello %s! Hi %s", 2, args[0], args[1]);
printf("%s\n", str_UUID);
for (size_t i = 0; i < 2; i++)
{
    free(args[i]);
}
free(str_UUID);
```

=> transpile with array holding stringified args and string with UUID, transpile statement using fstring then free all

# EOF

Check list of variables left and free them all