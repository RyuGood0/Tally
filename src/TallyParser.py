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
			"""
			Find last operation in math expression:
			1 + 2 * 3 => BinOp(1, '+', BinOp(2, '*', 3))
			3 *5/2 +1 => BinOp(BinOp(BinOp(3, '*', 5), '/', 2), "+", 1)
			"""

			# Find last operation in order of PEMDAS

			if any(tokens[i].type == "PLUS" or tokens[i].type == "MINUS" for i in range(len(tokens))):
				# Find last operation of type PLUS or MINUS outside of parentheses
				in_paren = False
				for i in range(len(tokens)-1, 0, -1):
					if tokens[i].type == "RPAREN":
						in_paren = True
					elif tokens[i].type == "LPAREN":
						in_paren = False
					if (tokens[i].type == "PLUS" or tokens[i].type == "MINUS") and not in_paren:
						return BinOp(parse_math(tokens[:i]), tokens[i].value, parse_math(tokens[i+1:]))
			if any(tokens[i].type == "MULT" or tokens[i].type == "DIV" for i in range(len(tokens))):
				# Find last operation of type MULT or DIV outside of parentheses

				in_paren = False
				for i in range(len(tokens)-1, 0, -1):
					if tokens[i].type == "RPAREN":
						in_paren = True
					elif tokens[i].type == "LPAREN":
						in_paren = False
					if (tokens[i].type == "MULT" or tokens[i].type == "DIV") and not in_paren:
						return BinOp(parse_math(tokens[:i]), tokens[i].value, parse_math(tokens[i+1:]))
			if any(tokens[i].type == "POWER" for i in range(len(tokens))):
				in_paren = False
				for i in range(len(tokens)-1, 0, -1):
					if tokens[i].type == "RPAREN":
						in_paren = True
					elif tokens[i].type == "LPAREN":
						in_paren = False
					if tokens[i].type == "POWER" and not in_paren:
						return BinOp(parse_math(tokens[:i]), tokens[i].value, parse_math(tokens[i+1:]))
			if any(tokens[i].type == "LPAREN" for i in range(len(tokens))):				
				# Find last parenthesis
				l_ind = None
				r_ind = None
				for i in range(len(tokens)-1, -1, -1):
					if tokens[i].type == "RPAREN":
						r_ind = i
					if tokens[i].type == "LPAREN":
						l_ind = i
						return parse_math(tokens[l_ind+1:r_ind])
			return tokens[0].value
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

# ===================== TESTING =====================
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

from treelib import Tree

def add_BinOps(tree, id, binop, depth):
	left = binop.left
	right = binop.right

	if isinstance(left, BinOp):
		tree.create_node(str(left), id + "l"* depth, parent=id)
		add_BinOps(tree, id + "l"* depth, left, depth+1)
	else:
		tree.create_node(str(left), id + "l"* depth, parent=id)

	if isinstance(right, BinOp):
		tree.create_node(str(right), id + "r"* depth, parent=id)
		add_BinOps(tree, id + "r"* depth, right, depth+1)
	else:
		tree.create_node(str(right), id + "r"* depth, parent=id)

def display_AST(ast):
	tree = Tree()

	tree.create_node("MAIN", "main")
	for i, child in enumerate(ast.main.children):
		tree.create_node(str(child), str(i), parent="main")
		if isinstance(child, BinOp):
			add_BinOps(tree, str(i), child, 1)

	tree.show()

display_AST(ast)