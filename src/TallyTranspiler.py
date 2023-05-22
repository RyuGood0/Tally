from TallyParser import TallyParser
from dataclasses import dataclass

def raise_error(comment):
    print(comment)
    exit()

@dataclass
class Variable:
    name: str
    type: str
    value: any
    constant: bool = False

class TallyTranspiler(object):
    parser = TallyParser()
    parser.build()

    variables = {}
    functions = {}

    imports = []
    func_decls = []

    def __call__(self, content):
        parsed = self.parser.parse(content)

        main_code = ""

        for statement in parsed[1]:
            if isinstance(statement, tuple) and statement[0] != 'func_decl':
                buffer = self.transpile(statement)
                main_code += buffer
                if not (buffer[-1] == ';' or buffer[-1] == '}'):
                    main_code += ';\n'
                else:
                    main_code += '\n'

        main_code = "".join([f"\t{code}\n" for code in main_code.splitlines()])

        include_code = ""
        for imps in self.imports:
            include_code += f"#include <{imps}.h>\n"

        func_decl_code = ""
        for func_decl in self.func_decls:
            func_decl_code += func_decl + "\n"

        c_code = f"{include_code}\n{func_decl_code}int main(int argc, char *argv[]) {{\n{main_code}}}"

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
            return statement
        elif isinstance(statement, str):
            return statement
        elif statement[0] == 'assign':
            if self.is_assigned(statement)[0]:
                if self.variables[statement[1]].constant:
                    raise_error(f"Cannot reassign constant {self.is_assigned(statement)[1].name}")
                return f"{self.is_assigned(statement)[1].name} = {self.transpile(statement[2])}"
            elif len(statement) == 3:
                self.variables[statement[1]] = Variable(statement[1], 'any', 0)
                return f"<TODO_TYPE> {statement[1]} = {self.transpile(statement[2])}"
            elif len(statement) == 4:
                self.variables[statement[2]] = Variable(statement[2], statement[1], 0)
                return f"{self.transpile_type(statement[1])} {statement[2]} = {self.transpile(statement[3])}"
        elif statement[0] == 'const_assign':
            if self.is_assigned(statement)[0]:
                raise_error(f"Constant {self.is_assigned(statement)[1].name} already assigned")
            print(statement)
            if len(statement) == 3:
                self.variables[statement[1]] = Variable(statement[1], 'any', 0, True)
                return f"const <TODO_TYPE> {statement[1]} = {self.transpile(statement[2])}"
            elif len(statement) == 4:
                self.variables[statement[2]] = Variable(statement[2], statement[1], 0, True)
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

if __name__ == '__main__':
    file_path = "examples/test.ta"
    with open(file_path, 'r') as file:
        data = file.read()
        tally = TallyTranspiler()
        c_code = tally(data)
        print(c_code)