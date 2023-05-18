from TallyParser import TallyParser

def raise_error(comment):
    print(comment)
    exit()

class ExecutionScope(object):
    def __init__(self):
        self.vars = {}
        self.functions = {}

    def execute_stack(self, stack):
        for statement in stack:
            self.execute(statement)

    def execute(self, statement):
        if isinstance(statement, int):
            return statement
        elif isinstance(statement, float):
            return statement
        elif statement[0] == 'id':
            return self.vars[statement[1]]
        elif statement[0] == 'array':
            return statement[1]
        elif statement[0] == '++':
            if statement[1] not in self.vars:
                raise_error(f"Variable {statement[1]} not declared")
            self.vars[statement[1]] += 1
        elif statement[0] == 'assign':
            if len(statement) == 3:
                self.vars[statement[1]] = self.execute(statement[2])
            elif len(statement) == 4:
                # Here you could check if the type of the right-hand side matches the declared type
                self.vars[statement[2]] = self.execute(statement[3])
        elif statement[0] == 'func_decl':
            self.functions[statement[1]] = statement[-1]
        elif statement[0] in ('+', '-', '*', '/', '**', '==', '!='):
            left = self.execute(statement[1])
            right = self.execute(statement[2])
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
            elif statement[0] == '==':
                return left == right
            elif statement[0] == '!=':
                return left != right
        elif statement[0] == 'func_call':
            if statement[1] == 'print':
                print(*[self.execute(arg) for arg in statement[2]])
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
    file_path = "examples/math.ta"
    with open(file_path, 'r') as file:
        data = file.read()
        tally = TallyInterpreter()
        tally(data)  # Test it