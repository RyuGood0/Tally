import ply.lex as lex

reserved = {
	'if' : 'IF',
	'else' : 'ELSE',
	'while' : 'WHILE',
	'for' : 'FOR',

	'return' : 'RETURN',
	'break' : 'BREAK',
	'continue' : 'CONTINUE',
	
	'import' : 'IMPORT',
	'importc' : 'IMPORTC',

	'string' : 'STRINGattr',
	'int' : 'INTattr',
	'float' : 'FLOATattr',
	'bool' : 'BOOLattr',
	'null' : 'NULLattr',

	'def' : 'DEF'
}

tokens = [
	'NUMBER',
	'FLOAT',
	'STRING',
	'ADD',
	'SUB',
	'PLUS',
	'MINUS',
	'MULT',
	'DIV',
	'LPAREN',
	'RPAREN',
	'LBRACE',
	'RBRACE',
	'EQUALS',
	'GREATER',
	'LESS',
	'GEQUAL',
	'LEQUAL',
	'ID',
	'ASSIGN',
	'LNEND',
	'COMMA'
] + list(reserved.values())

t_ADD = r'\+\+'
t_SUB = r'--'
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_MULT  = r'\*'
t_DIV  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_ASSIGN = r'='
t_EQUALS = r'=='
t_GREATER = r'>'
t_LESS = r'<'
t_GEQUAL = r'>='
t_LEQUAL = r'<='
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','

def t_NUMBER(t):
	r'(?<![\d.])[0-9]+(?![\d.])'
	t.value = int(t.value)
	return t

def t_FLOAT(t):
	r'\d+[,.]\d+|(\d+)'
	t.value = float(t.value)
	return t

def t_STRING(t):
	r'\"[^\"]*\"'
	t.value = t.value[1:-1]
	return t

def t_ID(t):
	r'[a-zA-Z_][a-zA-Z_0-9]*'
	t.type = reserved.get(t.value,'ID')
	return t

def t_COMMENT(t):
	r'\#.*'
	pass

def t_LNEND(t):
	r'\n+'
	t.lexer.lineno += len(t.value)
	return t

t_ignore  = ' \t'

def t_error(t):
	print("Illegal character '%s'" % t.value[0])
	t.lexer.skip(1)

def get_lexer():
	return lex.lex()

def export_tokens(lexer, output):
	token = lexer.token()
	tokens = []
	while token:
		tokens.append(token)
		token = lexer.token()
	with open(output, "w") as f:
		for token in tokens:
			f.write(f"{token}\n")