import ply.lex as lex

class LangLexer(object):
	reserved = {
		'if' : 'IF',
		'else' : 'ELSE',
		'while' : 'WHILE',
		'for' : 'FOR',
		'in' : 'IN',

		'return' : 'RETURN',
		'break' : 'BREAK',
		'continue' : 'CONTINUE',
		
		'import' : 'IMPORT',

		'const' : 'CONST',

		'str' : 'STRINGattr',
		'int' : 'INTattr',
		'float' : 'FLOATattr',
		'bool' : 'BOOLattr',

		'null' : 'NULL',

		'def' : 'DEF',
		'class': 'CLASS'
	}

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
		'NEQUAL',
		'ID',
		'ASSIGN',
		'LNEND',
		'COMMA',
		'BOOL',
		'LBRACKET', 
		'RBRACKET',
		'PLUSEQUAL',
		'MINUSEQUAL'
	] + list(reserved.values())

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
	t_NEQUAL = r'!='
	t_LBRACE = r'\{'
	t_RBRACE = r'\}'
	t_COMMA = r','
	t_RBRACKET = r'\]'
	t_LBRACKET = r'\['
	t_PLUSEQUAL = r'\+='
	t_MINUSEQUAL = r'-='

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

		if t.value in self.reserved:
			t.type = self.reserved[t.value]

		return t
	
	def t_newline(self,t):
		r'\n+'
		t.lexer.lineno += len(t.value)

	def t_COMMENT(self, t):
		r'\#.*'
		pass

	# A string containing ignored characters (spaces and tabs)
	t_ignore  = ' \t'

	# Error handling rule
	def t_error(self,t):
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

if __name__ == "__main__":
	# Build the lexer and try it out
	m = LangLexer()
	m.build()           # Build the lexer
	m.test(
		"""
		a = 4 + 5
		def add(a, b) {
			return a + b
		}

		b = "Hello"

		# Comment here
		float c = 3.14
		"""
	)     # Test it