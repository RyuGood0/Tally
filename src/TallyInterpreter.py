from TallyParser import TallyParser

def raise_error(comment):
    print(comment)
    exit()

from dataclasses import dataclass

@dataclass
class Variable:
    value: any
    type: str = 'any'
    const: bool = False

    def __repr__(self) -> str:
        return str(self.value)

@dataclass
class Function:
    vars: dict
    functions: dict
    parameters: list
    return_type: str
    body: list

class ExecutionScope(object):
    def __init__(self):
        self.vars = {} # entry example: 'x': Variable('int', 5)
        self.functions = {} # entry example: 'foo': Function({}, {}, [], 'any', [('func_call', 'print', [('id', 'x')])])

    def execute_stack(self, stack):
        for statement in stack:
            self.execute(statement)

    def execute(self, statement):
        if isinstance(statement, int):
            return statement
        elif isinstance(statement, float):
            return statement
        elif statement[0] == 'id':
            if statement[1] not in self.vars:
                raise_error(f"Variable {statement[1]} not defined")
            return self.vars[statement[1]]
        elif statement[0] == 'array':
            return statement[1]
        elif statement[0] == 'assign':
            if len(statement) == 3:
                if statement[1] in self.vars:
                    if self.vars[statement[1]].const:
                        raise_error(f"Cannot assign to constant {statement[1]}")
                    elif self.vars[statement[1]].type != 'any':
                        second_value = self.execute(statement[2])
                        if isinstance(second_value, Variable) and self.vars[statement[1]].type != second_value.type:
                            raise_error(f"Cannot assign '{self.execute(statement[2])}' of type {self.execute(statement[2]).type} to var of type {self.vars[statement[1]].type}")
                        elif self.vars[statement[1]].type != type(second_value):
                            raise_error(f"Cannot assign '{self.execute(statement[2])}' of type {type(self.execute(statement[2])).__name__} to var of type {self.vars[statement[1]].type}")

                self.vars[statement[1]] = Variable(self.execute(statement[2]))
            elif len(statement) == 4:
                if statement[2] in self.vars:
                    raise_error(f"Cannot assign to typed {statement[2]}")
                self.vars[statement[2]] = Variable(self.execute(statement[3]), statement[1])
        elif statement[0] == 'const_assign':
            if len(statement) == 3:
                if statement[1] in self.vars:
                    if self.vars[statement[1]].const:
                        raise_error(f"Cannot assign to constant {statement[1]}")
            if len(statement) == 3:
                self.vars[statement[1]] = Variable(self.execute(statement[2]), const=True)
            elif len(statement) == 4:
                self.vars[statement[2]] = Variable(self.execute(statement[3]), statement[1], True)
        elif statement[0] == 'func_decl':
            self.functions[statement[1]] = statement[-1]
        elif statement[0] in ('+', '-', '*', '/', '**'):
            left = self.execute(statement[1])
            right = self.execute(statement[2])

            if isinstance(left, Variable):
                left = left.value
            if isinstance(right, Variable):
                right = right.value

            if not isinstance(left, int) and not isinstance(left, float):
                raise_error(f"Left side of {statement[0]} is not of type int/float")

            if not isinstance(right, int) and not isinstance(right, float):
                raise_error(f"Right side of {statement} is not of type int/float")

            if statement[0] == '+':
                return left + right
            elif statement[0] == '-':
                return left - right
            elif statement[0] == '*':
                return left * right
            elif statement[0] == '/':
                return left / right
            elif statement[0] == '**':
                return left ** right
        elif statement[0] in ('==', '!=', '>', '<', '>=', '<='):
            left = self.execute(statement[1])
            right = self.execute(statement[2])

            if isinstance(left, Variable):
                left = left.value
            if isinstance(right, Variable):
                right = right.value

            if statement[0] == '==':
                return left == right
            elif statement[0] == '!=':
                return left != right
            elif statement[0] == '>':
                return left > right
            elif statement[0] == '<':
                return left < right
            elif statement[0] == '>=':
                return left >= right
            elif statement[0] == '<=':
                return left <= right
        elif statement[0] == 'func_call':
            if statement[1] == 'print':
                print(*[self.execute(arg) for arg in statement[2]], sep=', ')
            else:
                if statement[1] not in self.functions:
                    raise_error(f"Function {statement[1]} not declared")
                for sub_statement in self.functions[statement[1]]:
                    self.execute(sub_statement)
        elif statement[0] == 'if':
            if self.execute(statement[1]):
                for sub_statement in statement[2]:
                    self.execute(sub_statement)
        elif statement[0] == 'if_else':
            if self.execute(statement[1]):
                for sub_statement in statement[2]:
                    self.execute(sub_statement)
            else:
                for sub_statement in statement[3]:
                    self.execute(sub_statement)
        elif statement[0] == 'for_in':
            for element in self.execute(statement[2]):
                self.vars[statement[1][1]] = element
                for sub_statement in statement[3]:
                    self.execute(sub_statement)

        elif isinstance(statement, str):
            return statement

class TallyInterpreter(object):
    parser = TallyParser()
    parser.build()

    def __call__(self, content):
        parsed = self.parser.parse(content)
        
        base_scope = ExecutionScope()
        base_scope.execute_stack(parsed[1])

if __name__ == '__main__':
    file_path = "examples/vars.ta"
    with open(file_path, 'r') as file:
        data = file.read()
        tally = TallyInterpreter()
        tally(data)  # Test it