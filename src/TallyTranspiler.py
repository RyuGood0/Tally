from TallyParser import TallyParser
from dataclasses import dataclass

def raise_error(comment):
    print(comment)
    exit()

@dataclass
class Variable:
    name: str
    type: int
    value: any
    constant: bool = False

structs = {
    'dynamic_type': "typedef struct dynamic_type {\n\tuint8_t type;\n\tvoid* value;\n} dynamic_t;\n"
}

dynamic_type_map = {
    'int': 0,
    'float': 1,
    'str': 2,
    'any': 3
}

class TallyTranspiler(object):
    parser = TallyParser()
    parser.build()

    variables = {}
    functions = {}

    imports = []
    func_decls = []
    structs = []

    def __call__(self, content):
        parsed = self.parser.parse(content)

        main_code = ""

        functions_code = ""

        for statement in parsed[1]:
            if isinstance(statement, tuple) and (statement[0] != 'func_decl' and statement[0] != 'typed_func_decl'):
                buffer = self.transpile(statement)
                main_code += buffer
                if not (buffer[-1] == ';' or buffer[-1] == '}'):
                    main_code += ';\n'
                else:
                    main_code += '\n'
            elif statement[0] == 'func_decl' or statement[0] == 'typed_func_decl':
                buffer = self.transpile(statement)
                functions_code += buffer
                if not (buffer[-1] == ';' or buffer[-1] == '}'):
                    functions_code += ';\n\n'
                else:
                    functions_code += '\n\n'

        main_code = "".join([f"\t{code}\n" for code in main_code.splitlines()])

        include_code = ""
        for imps in self.imports:
            include_code += f"#include <{imps}.h>\n"

        func_decl_code = ""
        for func_decl in self.func_decls:
            func_decl_code += func_decl + "\n"

        structs_code = ""
        for struct in self.structs:
            structs_code += structs[struct] + "\n"

        c_code = f"{include_code}\n{func_decl_code}\n{structs_code}\n{functions_code}\nint main(int argc, char *argv[]) {{\n{main_code}}}"

        return c_code
    
    def is_assigned(self, statement):
        if statement[0] == 'assign':
            if len(statement) == 3 and statement[1] in self.variables:
                return True, self.variables[statement[1]]
            elif len(statement) == 4 and statement[2] in self.variables:
                return True, self.variables[statement[2]]
        return False, None

    def transpile(self, statement):
        if isinstance(statement, int):
            return str(statement)
        
        elif isinstance(statement, float):
            return str(statement)
        
        elif isinstance(statement, str):
            return statement
        
        elif statement[0] == 'assign':
            if self.is_assigned(statement)[0]:
                if self.variables[statement[1]].constant:
                    raise_error(f"Cannot reassign constant {self.is_assigned(statement)[1].name}")
                return f"{self.is_assigned(statement)[1].name} = {self.transpile(statement[2])}"
            elif len(statement) == 3:
                if not isinstance(statement[2], tuple):
                    d_type = self.get_inferred_type(statement[2])
                    self.variables[statement[1]] = Variable(statement[1], dynamic_type_map[d_type], 0)
                    if 'dynamic_type' not in self.structs:
                        self.structs.append('dynamic_type')
                        self.imports.append("stdint")
                else:
                    d_type = self.get_inferred_type(statement[2])
                    self.variables[statement[1]] = Variable(statement[1], dynamic_type_map[d_type], 0)

                right_member = self.transpile(statement[2])

                return f"dynamic_t {statement[1]} = {{.type = {dynamic_type_map[d_type]}, .value = {right_member}}};"
            elif len(statement) == 4:
                self.variables[statement[2]] = Variable(statement[2], dynamic_type_map[statement[1]], 0)
                if isinstance(statement[3], str):
                    return f"{self.transpile_type(statement[1])} {statement[2]} = \"{self.transpile(statement[3])}\";"
                return f"{self.transpile_type(statement[1])} {statement[2]} = {self.transpile(statement[3])};"
            
        elif statement[0] == 'const_assign':
            if self.is_assigned(statement)[0]:
                raise_error(f"Constant {self.is_assigned(statement)[1].name} already assigned")
            if len(statement) == 3:
                if not isinstance(statement[2], tuple):
                    d_type  = self.get_inferred_type(statement[2])
                    self.variables[statement[1]] = Variable(statement[1], dynamic_type_map[d_type], 0, True)
                    if 'dynamic_type' not in self.structs:
                        self.structs.append('dynamic_type')
                        self.imports.append("stdint")
                else:
                    d_type = self.get_inferred_type(statement[2])
                    self.variables[statement[1]] = Variable(statement[1], dynamic_type_map[d_type], 0, True)

                right_member = self.transpile(statement[2])

                return f"dynamic_t {statement[1]} = {{.type = {dynamic_type_map[d_type]}, .value = {right_member}}};"
            elif len(statement) == 4:
                self.variables[statement[2]] = Variable(statement[2], dynamic_type_map[statement[1]], 0, True)
                if isinstance(statement[3], str):
                    return f"{self.transpile_type(statement[1])} {statement[2]} = \"{self.transpile(statement[3])}\";"
                return f"const {self.transpile_type(statement[1])} {statement[2]} = {self.transpile(statement[3])}"
            
        elif statement[0] in ('+', '-', '*', '/', '**'):
            left = self.transpile(statement[1])
            right = self.transpile(statement[2])
            if statement[0] == '+':
                return f"{left} + {right}"
            elif statement[0] == '-':
                return f"{left} - {right}"
            elif statement[0] == '*':
                return f"{left} * {right}"
            elif statement[0] == '/':
                return f"{left} / {right}"
            elif statement[0] == '**':
                if 'math' not in self.imports:
                    self.imports.append('math')
                return f"pow({left}, {right})"
            
        elif statement[0] in ('>', '<', '>=', '<=', '=='):
            left = self.transpile(statement[1])
            right = self.transpile(statement[2])
            if statement[0] == '>':
                return f"{left} > {right}"
            elif statement[0] == '<':
                return f"{left} < {right}"
            elif statement[0] == '>=':
                return f"{left} >= {right}"
            elif statement[0] == '<=':
                return f"{left} <= {right}"
            elif statement[0] == '==':
                return f"{left} == {right}"
            
        elif statement[0] == 'id':
            return statement[1]
        
        elif statement[0] == "if":
            buffer = f"if ({self.transpile(statement[1])}) {{\n"
            for sub_statement in statement[2]:
                buffer += "\t" + self.transpile(sub_statement) + ";\n"
            buffer += "}"
            return buffer
        
        elif statement[0] == "if_else":
            buffer = f"if ({self.transpile(statement[1])}) {{\n"
            for sub_statement in statement[2]:
                buffer += "\t" + self.transpile(sub_statement) + ";\n"
            buffer += "} else {\n"
            for sub_statement in statement[3]:
                buffer += "\t" + self.transpile(sub_statement) + ";\n"
            buffer += "}"
            return buffer
        
        elif statement[0] == "func_call":
            if statement[1] == "print":
                if 'stdio' not in self.imports:
                    self.imports.append('stdio')

                buffer = "printf(\""
                vars_to_format = []
                for arg in statement[2]:
                    if isinstance(arg, str):
                        buffer += arg
                    elif arg[0] == 'id':
                        vars_to_format.append(arg[1])
                        if self.variables[arg[1]].type == 0:
                            buffer += "%d"
                        elif self.variables[arg[1]].type == 1:
                            buffer += "%f"
                        elif self.variables[arg[1]].type == 2:
                            buffer += "%s"

                buffer += "\""
                for var in vars_to_format:
                    buffer += f", {var}"
                buffer += ")"

                return buffer
            
            elif statement[1] == "println":
                if 'stdio' not in self.imports:
                    self.imports.append('stdio')

                buffer = "printf(\""
                vars_to_format = []
                for arg in statement[2]:
                    if isinstance(arg, str):
                        buffer += arg
                    elif arg[0] == 'id':
                        vars_to_format.append(arg[1])
                        if self.variables[arg[1]].type == 0:
                            buffer += "%d"
                        elif self.variables[arg[1]].type == 1:
                            buffer += "%f"
                        elif self.variables[arg[1]].type == 2:
                            buffer += "%s"

                buffer += "\\n\""
                for var in vars_to_format:
                    buffer += f", {var}"
                buffer += ")"

                return buffer

            elif statement[1] in self.functions:
                return f"{statement[1]}({', '.join([self.transpile(arg) for arg in statement[2]])})"
            
            raise ValueError(f'No such function: {statement}')
        
        elif statement[0] == 'func_decl':
            func_name = statement[1]
            func_args = statement[2]
            func_body = statement[3]

            self.functions[func_name] = {
                "args": func_args,
                "body": func_body,
                "type": 'any'
            }

            has_return = False
            for sub_statement in func_body:
                if sub_statement[0] == 'return':
                    has_return = True
                    break

            if not has_return:
                buffer = f"void {func_name}({', '.join([self.transpile_type(arg[1]) + ' ' + arg[2] for arg in func_args])}) {{\n"
            else:
                buffer = f"dynamic_t* {func_name}({', '.join([self.transpile_type(arg[1]) + ' ' + arg[2] for arg in func_args])}) {{\n"

            for sub_statement in func_body:
                buffer += "\t" + self.transpile(sub_statement) + ";\n"

            buffer += "}"

            return buffer

        elif statement[0] == 'typed_func_decl':
            func_name = statement[2]
            func_args = statement[3]
            func_body = statement[4]

            self.functions[func_name] = {
                "args": func_args,
                "body": func_body,
                "type": statement[1]
            }

            buffer = f"{self.transpile_type(statement[1])} {func_name}("

            for arg in func_args:
                if len(arg) == 2:
                    buffer += f"dynamic_t* {arg[1]}, "
                else:
                    buffer += f"{self.transpile_type(arg[1])} {arg[2]}, "

            buffer = buffer[:-2] + ") {\n"

            for sub_statement in func_body:
                buffer += "\t" + self.transpile(sub_statement) + ";\n"

            buffer += "}"

            return buffer
        
        elif statement[0] == 'return':
            return f"return {self.transpile(statement[1])}"

        else:
            raise ValueError(f'Cannot transpile: {statement}')

    def transpile_type(self, type_name):
        if type_name == 'int':
            return 'int'
        elif type_name == 'float':
            return 'float'
        elif type_name == 'str':
            return 'char*'
        else:
            raise ValueError(f'Cannot transpile type: {type_name}')
        
    def get_inferred_type(self, statement):
        if isinstance(statement, int):
            return 'int'
        elif isinstance(statement, float):
            return 'float'
        elif statement[0] == "func_call":
            # check return type of function
            return self.functions[statement[1]]['type']
        return 'any'

if __name__ == '__main__':
    file_path = "examples/test.ta"
    with open(file_path, 'r') as file:
        data = file.read()
        tally = TallyTranspiler()
        c_code = tally(data)
        print(c_code)

    run = True

    if run:
        with open("temp.c", "w") as f:
            f.write(c_code)

        import subprocess
        subprocess.Popen("gcc ../temp.c -o out")
        subprocess.Popen("./out")
