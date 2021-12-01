from TallyTokenizer import lexer

class AST:
	def __init__(self):
		self.main = Node("main")

	def __repr__(self) -> str:
		return self.main.__repr__()

class Node:
	def __init__(self, type):
		self.type = type
		self.children = []

	def __repr__(self):
		if len(self.children) == 0:
			return '<{}>'.format(self.type)
		else:
			s = ''.join(c.__repr__() + ", " for c in self.children)
			return f'<{self.type}> with children: ' + s[:-2]

class BinOp(Node):
	"""
	Can represent any form of expression with a left and right child such as mathimatical expressions, variable assignments, etc.
	"""
	def __init__(self, left, op, right):
		super().__init__('BinOp')
		self.left = left
		self.op = op
		self.right = right

	def __repr__(self):
		return f'{self.type}: {self.left} ({self.op}) {self.right}'

class FonctionCall(Node):
	def __init__(self, name, args):
		super().__init__('FonctionCall')
		self.name = name
		self.args = args

def parse_math(tokens):
	if tokens[0].type == "NUMBER" or tokens[0].type == "ID" or tokens[0].type == "LPAREN" or tokens[0].type == "FLOAT":
		if len(tokens) == 3:
			return BinOp(tokens[0].value, tokens[1].value, tokens[2].value)
		else:
			print([token.value for token in tokens])
	else:
		raise Exception(f"Invalid token {tokens[0].value} on line {tokens[0].lineno}")

def parse_id(tokens):
	if tokens[0].type == 'ID':
		if not (tokens[1].type == 'ASSIGN' or tokens[1].type == 'ADD' or tokens[1].type == 'SUB'):
			raise Exception(f"Invalid token {tokens[1].value} on line {tokens[1].lineno}")
		if len(tokens) == 3 and tokens[1].type == "ASSIGN":
			return BinOp(tokens[0].value, "ASSIGN", tokens[2].value)
		elif len(tokens) == 2 and (tokens[1].type == "ADD" or tokens[1].type == "SUB"):
			add_bin = BinOp(tokens[0].value, "+", 1 if tokens[1].type == "ADD" else -1)
			return BinOp(tokens[0].value, "ASSIGN", add_bin)
		return BinOp(tokens[0].value, 'ASSIGN', parse_math(tokens[2:]))
	else:
		raise Exception('Expected ID')

data = open("tests/math.ta", "r").read()

lexer.input(data)

ast = AST()
tok = lexer.token()
while True:
	if tok.type == "ID":
		line_tokens = [tok]
		while True:
			tok = lexer.token()
			if not tok or tok.lineno != line_tokens[0].lineno:
				break
			line_tokens.append(tok)
		ast.main.children.append(parse_id(line_tokens))
	
	elif tok.type == "IF":
		pass

	if not tok: 
		break

print(ast)