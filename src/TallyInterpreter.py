from TallyParser import TallyParser

class TallyInterpreter(object):
    parser = TallyParser()
    parser.build()

    def __call__(self, content):
        parsed = self.parser.parse(content)
        
        self.vars = {}
        self.functions = {}

        for statement in parsed[1]:
            self.execute(statement)

    def execute(self, statement):
        if isinstance(statement, int):
            return statement
        elif isinstance(statement, float):
            return statement
        elif statement[0] == 'id':
            return self.vars[statement[1]]
        elif statement[0] == '++':
            self.vars[statement[1]] += 1
        elif statement[0] == 'assign':
            if len(statement) == 3:
                self.vars[statement[1]] = self.execute(statement[2])
            elif len(statement) == 4:
                # Here you could check if the type of the right-hand side matches the declared type
                self.vars[statement[2]] = self.execute(statement[3])
        elif statement[0] in ('+', '-', '*', '/', '**', '=='):
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
        elif statement[0] == 'func_call':
            if statement[1] == 'print':
                buffer = ""
                for arg in statement[2]:
                    buffer += str(self.execute(arg)) + ", "
                print(buffer[:-2])

        elif isinstance(statement, str):
            return statement

if __name__ == '__main__':
    file_path = "examples/math.ta"
    """ math.ta content:
    int a = 5
    b = 5 + 6*2/3 - 1

    d = (1+2) * (3+4)

    a++
    a++
    c = a+b
    e = (2**(2+3))
    """
    with open(file_path, 'r') as file:
        data = file.read()
        tally = TallyInterpreter()
        tally(data)  # Test it