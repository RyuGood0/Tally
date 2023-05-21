from TallyParser import TallyParser
from dataclasses import dataclass

@dataclass
class Variable:
    name: str
    type: str
    value: any

class TallyTranspiler(object):
    parser = TallyParser()
    parser.build()

    variables = {}
    functions = {}

    def __call__(self, content):
        parsed = self.parser.parse(content)

        c_code = ""

        for statement in parsed[1]:
            buffer = self.transpile(statement)
            c_code += buffer
            if not (buffer[-1] == ';' or buffer[-1] == '}'):
                c_code += ';\n'

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
                return f"{self.is_assigned(statement)[1].name} = {self.transpile(statement[2])}"
            elif len(statement) == 3:
                self.variables[statement[1]] = Variable(statement[1], 'int', 0)
                return f"int {statement[1]} = {self.transpile(statement[2])}"
            elif len(statement) == 4:
                self.variables[statement[2]] = Variable(statement[2], 'int', 0)
                return f"{self.transpile_type(statement[1])} {statement[2]} = {self.transpile(statement[3])}"
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