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

	'const' : 'CONST',

	'str' : 'STRINGattr',
	'int' : 'INTattr',
	'float' : 'FLOATattr',
	'bool' : 'BOOLattr',
	'null' : 'NULLattr',

	'def' : 'DEF',
	'class': 'CLASS'
}

class MyLexer(object):
	reserved = reserved

	tokens = [
		'NUMBER',
		'FLOAT',
		'STRING',
		'ADD',
		'SUB',
		'PLUS',
		'MINUS',
		'EXP',
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

	# Regular expression rules for simple tokens
	t_ADD = r'\+\+'
	t_SUB = r'--'
	t_PLUS    = r'\+'
	t_MINUS   = r'-'
	t_EXP  = r'\*\*'
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

	def t_NUMBER(self, t):
		r'(?<![\d.])[0-9]+(?![\d.])'
		t.value = int(t.value)
		return t

	def t_FLOAT(self, t):
		r'\d+[,.]\d+|(\d+)'
		t.value = float(t.value)
		return t

	def t_STRING(self, t):
		r'\"[^\"]*\"'
		t.value = t.value[1:-1]
		return t

	def t_ID(self, t):
		r'[a-zA-Z_][a-zA-Z_0-9]*'
		t.type = reserved.get(t.value,'ID')
		return t

	def t_COMMENT(self, t):
		r'\#.*'
		pass

	def t_newline(self, t):
		r'\n+'
		t.lexer.lineno += len(t.value)

	t_ignore  = ' \t'

	def t_error(t):
		print("Illegal character '%s'" % t.value[0])
		t.lexer.skip(1)

	# Build the lexer
	def build(self,**kwargs):
		self.lexer = lex.lex(module=self, **kwargs)
	
	# Test it output
	def test(self,data):
		self.lexer.input(data)
		while True:
			tok = self.lexer.token()
			if not tok: 
				break
			print(tok)

# Build the lexer and try it out
m = MyLexer()
m.build()           # Build the lexer
m.test("3 + 4")     # Test it