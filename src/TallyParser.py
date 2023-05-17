import ply.yacc as yacc
from TallyTokenizer import get_lexer

def p_program(p):
    '''
    program : statement_list
    '''
    p[0] = p[1]

def p_statement_list(p):
    '''
    statement_list : statement
                   | statement_list statement
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_statement(p):
    '''
    statement : assignment
              | function_declaration
              | function_call
              | if_statement
              | print_statement
    '''
    p[0] = p[1]

def p_assignment(p):
    '''
    assignment : ID ASSIGN expression LNEND
    '''
    p[0] = ('assign', p[1], p[3])

def p_expression(p):
    '''
    expression : NUMBER
               | FLOAT
               | STRING
               | ID
    '''
    p[0] = p[1]

def p_function_declaration(p):
    '''
    function_declaration : DEF ID LPAREN params RPAREN LBRACE statement_list RBRACE LNEND
    '''
    p[0] = ('func_decl', p[2], p[4], p[7])

def p_params(p):
    '''
    params : ID
           | params COMMA ID
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_function_call(p):
    '''
    function_call : ID LPAREN args RPAREN LNEND
    '''
    p[0] = ('func_call', p[1], p[3])

def p_args(p):
    '''
    args : expression
         | args COMMA expression
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_if_statement(p):
    '''
    if_statement : IF LPAREN expression RPAREN LBRACE statement_list RBRACE LNEND
    '''
    p[0] = ('if', p[3], p[6])

def p_print_statement(p):
    '''
    print_statement : PRINT LPAREN expression RPAREN LNEND
    '''
    p[0] = ('print', p[3])

def p_error(p):
    print("Syntax error at '%s'" % p.value)

def get_parser():
    return yacc.yacc()