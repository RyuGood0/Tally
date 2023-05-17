import ply.yacc as yacc
from TallyLexer import LangLexer

class MyParser(object):
    tokens = LangLexer().tokens

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
                | for_statement
        '''
        p[0] = p[1]

    def p_function_call(self, p):
        '''
        function_call : ID LPAREN RPAREN
                      | ID LPAREN parameters RPAREN
        '''
        if len(p) == 4:
            p[0] = ('func_call', p[1], [])
        else:
            p[0] = ('func_call', p[1], p[3])

    def p_if_statement(self, p):
        '''
        if_statement : IF expression LBRACE statement_body RBRACE
                    | IF expression LBRACE statement_body RBRACE ELSE LBRACE statement_body RBRACE
        '''
        if len(p) == 6:
            p[0] = ('if', p[2], p[4])
        else:
            p[0] = ('if_else', p[2], p[4], p[8])

    def p_for_statement(self, p):
        '''
        for_statement : FOR expression LBRACE statement_body RBRACE
        '''
        p[0] = ('for', p[2], p[4])

    def p_assignment(self, p):
        '''
        assignment : ID ASSIGN expression
                   | FLOATattr ID ASSIGN expression
                   | STRINGattr ID ASSIGN expression
                   | INTattr ID ASSIGN expression
                   | BOOLattr ID ASSIGN expression
        '''
        if len(p) == 4:
            p[0] = ('assign', p[1], p[3])
        else:
            p[0] = ('assign', p[1], p[2], p[4])

    def p_expression(self, p):
        '''
        expression : expression PLUS expression
                   | expression MINUS expression
                   | expression MULT expression
                   | expression DIV expression
                   | expression EXP expression
                   | expression EQUALS expression
                   | NUMBER
                   | STRING
                   | FLOAT
                   | ID
                   | function_call
        '''
        if len(p) == 2:
            p[0] = p[1]
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

    def p_return_type(self, p):
        '''
        return_type : INTattr
                    | FLOATattr
                    | STRINGattr
                    | BOOLattr
                    | NULL
        '''
        p[0] = p[1]

    def p_function_declaration(self, p):
        '''
        function_declaration : DEF ID LPAREN RPAREN LBRACE statement_body RBRACE
                            | DEF ID LPAREN parameters RPAREN LBRACE statement_body RBRACE
                            | DEF return_type ID LPAREN RPAREN LBRACE statement_body RBRACE
                            | DEF return_type ID LPAREN parameters RPAREN LBRACE statement_body RBRACE
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

    def p_statement_body(self, p):
        '''
        statement_body : statement_list
                    | return_statement
        '''
        if isinstance(p[1], list):
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_parameters(self, p):
        '''
        parameters : ID
                   | ID COMMA parameters
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_error(self, p):
        if p:
            print(f"Syntax error at token '{p.value}' on line {p.lineno}")
        else:
            print("Syntax error at EOF")

    def build(self, **kwargs):
        self.lexer = LangLexer()
        self.lexer.build()
        self.parser = yacc.yacc(module=self, **kwargs)

    def test(self, data):
        result = self.parser.parse(data, lexer = self.lexer.lexer)
        return result


# Build the parser and try it out
m = MyParser()
m.build()
print(m.test(
    """
    a = 4 + 5
    if a == 9 {
        print(a)
    } else {
        print("a is not 9")
    }

    b = [1, 2, 3, 4, 5]
    for i in b {
        print(i)
    }
    """
))  # Test it
