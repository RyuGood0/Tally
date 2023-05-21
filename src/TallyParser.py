import ply.yacc as yacc
from TallyLexer import TallyLexer

class TallyParser(object):
    tokens = TallyLexer().tokens

    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULT', 'DIV'),
        ('right', 'UMINUS'),
    )

    def p_program(self, p):
        '''
        program : statement_list
        '''
        p[0] = ('program', p[1])

    def p_statement_list(self, p):
        '''
        statement_list : statement
                       | statement_list statement
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_statement(self, p):
        '''
        statement : assignment
                | function_declaration
                | return_statement
                | function_call
                | if_statement
                | for_in_statement
        '''
        p[0] = p[1]

    def p_array_declaration(self, p):
        '''
        array_declaration : LBRACKET array_elements RBRACKET
        '''
        p[0] = ('array', p[2])

    def p_array_elements(self, p):
        '''
        array_elements : expression
                       | expression COMMA array_elements
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def _get_statement_line(self, p):
        return p.lineno(1)

    def p_if_statement(self, p):
        '''
        if_statement : IF expression LBRACE statement_list RBRACE
                    | IF expression LBRACE statement_list RBRACE ELSE LBRACE statement_list RBRACE
                    | IF LPAREN expression RPAREN LBRACE statement_list RBRACE
                    | IF LPAREN expression RPAREN LBRACE statement_list RBRACE ELSE LBRACE statement_list RBRACE
        '''
        if len(p) == 6:
            p[0] = ('if', p[2], p[4], self._get_statement_line(p))
        elif len(p) == 10:
            p[0] = ('if_else', p[2], p[4], p[8], self._get_statement_line(p))
        elif len(p) == 8:
            p[0] = ('if', p[3], p[6], self._get_statement_line(p))
        else:
            p[0] = ('if_else', p[3], p[6], p[10], self._get_statement_line(p))


    def p_for_in_statement(self, p):
        '''
        for_in_statement : FOR id_list IN ID LBRACE statement_list RBRACE
        '''
        p[0] = ('for_in', p[2], p[4], p[6], self._get_statement_line(p))

    def p_id_list(self, p):
        '''
        id_list : ID
                | ID COMMA id_list
        '''
        if len(p) == 2:
            p[0] = ('id', p[1])
        else:
            p[0] = ('id', p[1]) + p[3]

    def p_assignment_type(self, p):
        '''
        assignment_type : ASSIGN
                  | PLUSEQUAL
                  | MINUSEQUAL
        '''
        p[0] = p[1]

    def p_assignment(self, p):
        '''
        assignment : ID assignment_type expression
                   | ID ADD
                   | ID SUB
                   | type_attr ID ASSIGN expression
                   | CONST ID ASSIGN expression
                   | CONST type_attr ID ASSIGN expression
        '''
        if len(p) == 3:
            p[0] = ('assign', p[1], ('+' if p[2]=='++' else '-', ('id', p[1]), 1))
        elif p[2] == '=':
            p[0] = ('assign', p[1], p[3])
        elif p[2] == '+=':
            p[0] = ('assign', p[1], ('+', ('id', p[1]), p[3]))
        elif p[2] == '-=':
            p[0] = ('assign', p[1], ('-', ('id', p[1]), p[3]))
        elif len(p) == 5:
            if p[1] == 'const':
                p[0] = ('const_assign', p[2], p[4])
            else:
                p[0] = ('assign', p[1], p[2], p[4])
        else:
            p[0] = ('const_assign', p[2], p[3], p[5])


    def p_expression(self, p):
        '''
        expression : expression PLUS expression
                   | expression MINUS expression
                   | expression MULT expression
                   | expression DIV expression
                   | expression EXP expression
                   | expression EQUALS expression
                   | expression GREATER expression
                   | expression LESS expression
                   | expression GEQUAL expression
                   | expression LEQUAL expression
                   | expression NEQUAL expression
                   | LPAREN expression RPAREN
                   | NUMBER
                   | STRING
                   | FLOAT
                   | BOOL
                   | NULL
                   | id
                   | function_call
                   | array_declaration
        '''
        if len(p) == 2:
            p[0] = p[1]
        elif p[1] == '(':
            p[0] = p[2]
        else:
            p[0] = (p[2], p[1], p[3])

    def p_expression_uminus(self, p):
        'expression : MINUS expression %prec UMINUS'
        p[0] = -p[2]

    def p_return_statement(self, p):
        '''
        return_statement : RETURN expression
        '''
        p[0] = ('return', p[2])

    def p_type_attr(self, p):
        '''
        type_attr : INTattr
                    | FLOATattr
                    | STRINGattr
                    | BOOLattr
                    | NULL
        '''
        p[0] = p[1]

    def p_function_declaration(self, p):
        '''
        function_declaration : DEF ID LPAREN RPAREN LBRACE statement_list RBRACE
                            | DEF ID LPAREN func_parameters RPAREN LBRACE statement_list RBRACE
                            | DEF type_attr ID LPAREN RPAREN LBRACE statement_list RBRACE
                            | DEF type_attr ID LPAREN func_parameters RPAREN LBRACE statement_list RBRACE
        '''
        if len(p) == 8:
            p[0] = ('func_decl', p[2], [], p[6])
        elif len(p) == 9:
            if p[3] == '(':
                p[0] = ('func_decl', p[2], p[4], p[7])
            else:
                p[0] = ('func_decl', p[2], p[3], [], p[7])
        else:
            p[0] = ('func_decl', p[2], p[3], p[5], p[8])

    def p_function_call(self, p):
        '''
        function_call : ID LPAREN RPAREN
                      | ID LPAREN parameters RPAREN

        '''
        if len(p) == 4:
            p[0] = ('func_call', p[1], [])
        else:
            p[0] = ('func_call', p[1], p[3])

    def p_id(self, p):
        '''
        id : ID
        '''
        p[0] = ('id', p[1])

    def p_parameters(self, p):
        '''
        parameters : expression
                   | expression COMMA parameters
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_func_parameters(self, p):
        '''
        func_parameters : ID
                        | ID COMMA func_parameters
                        | type_attr ID
                        | type_attr ID COMMA func_parameters
        '''
        if len(p) == 2:
            p[0] = ['param', p[1]]
        elif len(p) == 3:
            p[0] = ['typed_param', p[1], p[2]]
        elif len(p) == 4:
            p[0] = [['param', p[1]]] + [p[3]]
        else:
            p[0] = [['typed_param', p[1], p[2]]] + [p[4]]

    def p_error(self, p):
        if p:
            print(f"Syntax error at token '{p.value}' on line {p.lineno}")
        else:
            print("Syntax error at EOF")

    def build(self, **kwargs):
        self.lexer = TallyLexer()
        self.lexer.build()
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, data):
        result = self.parser.parse(data, lexer = self.lexer.lexer)
        return result

if __name__ == '__main__':
    # Build the parser and try it out
    m = TallyParser()
    m.build()

    file_path = "examples/math.ta"
    with open(file_path, 'r') as file:
        data = file.read()
        parsed = m.parse(data)  # Test it

    for item in parsed[1]:
        print(item)