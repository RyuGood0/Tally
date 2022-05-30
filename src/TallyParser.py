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
			s = ''.join(c.__repr__() + "\n" for c in self.children)
			return f'<{self.type}> with children: \n' + s[:-1]

class Attribute:
	def __init__(self, type):
		self.type = type

class BinOp(Node):
	"""
	Can represent any form of expression with a left and right child such as mathimatical expressions, variable assignments, etc.
	"""
	def __init__(self, left, op, right):
		super().__init__("BinOp")
		self.left = left
		self.op = op
		self.right = right

	def __repr__(self):
		return f'{self.type}: {self.left} ({self.op}) {self.right}'

class VarStatement(Node):
	def __init__(self, name, value):
		super().__init__("VarStatement")
		self.name = name
		self.value = value
		self.attr = []

	def add_attr(self, attr):
		self.attr.append(attr)

	def __repr__(self):
		if len(self.attr) != 0:
			s_attrs = ', '.join(f'{a.type} ' for a in self.attr)
			return f'{self.name} = {self.value} ; ' + s_attrs
		return f'{self.name} = {self.value}'

class IfStatement(Node):
	def __init__(self, condition, body):
		super().__init__("IfStatement")
		self.condition = condition

class FunctionArgument(Node):
	def __init__(self, name, value, isCall):
		super().__init__("FunctionArgument")
		self.name = name
		self.value = value
		self.type = None
		self.isCall = isCall

	def __repr__(self):
		if self.type is not None:
			return f'{self.type} {self.name} = {self.value}'
		return f'{self.name} = {self.value}'

class FunctionDeclaration(Node):
	def __init__(self, name):
		super().__init__("FunctionDeclaration")
		self.name = name
		self.body = Node(name)
		self.attr = []
		self.args = []

	def add_attr(self, attr):
		self.attr.append(attr)

	def add_arg(self, arg):
		self.args.append(arg)

	def __repr__(self):
		s_args = ', '.join(f'{a.name}' for a in self.args)
		if len(self.attr) != 0:
			s_attrs = ', '.join(f'{a.type} ' for a in self.attr)
			return f'{self.name}({s_args}) ; ' + s_attrs
		return f'{self.name}({s_args})'

class CallStatement(Node):
	def __init__(self, name):
		super().__init__("CallStatement")
		self.name = name
		self.args = []

	def add_arg(self, arg):
		self.args.append(arg)

class Parser:
	def __init__(self, lexer):
		self.lexer = lexer
		self.current_token = lexer.token()
		self.next_token = lexer.token()
		self.ast = AST()

	def get_next_token(self):
		self.current_token = self.next_token
		self.next_token = self.lexer.token()
	
	def check_current_token(self, token_type):
		return self.current_token.type == token_type
	
	def check_next_token(self, token_type):
		return self.next_token.type == token_type

	def eat_token(self, token_type):
		if isinstance(token_type, list):
			if self.current_token.type in token_type:
				self.get_next_token()
		elif self.next_token.type == token_type:
			self.get_next_token()
		else:
			raise Exception(f"Expected {token_type} but got {self.next_token.type}")

	def get_line(self):
		line_tokens = [self.current_token]
		while True:
			self.get_next_token()
			if not self.current_token or self.current_token.lineno != line_tokens[0].lineno or self.current_token.type == 'LNEND':
				break
			line_tokens.append(self.current_token)

		return line_tokens

	def parse_math(self, tokens):
		if tokens[0].type == "NUMBER" or tokens[0].type == "ID" or tokens[0].type == "LPAREN" or tokens[0].type == "FLOAT":
			if len(tokens) == 3:
				return BinOp(tokens[0].value, tokens[1].value, tokens[2].value)

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
						return BinOp(self.parse_math(tokens[:i]), tokens[i].value, self.parse_math(tokens[i+1:]))
			if any(tokens[i].type == "MULT" or tokens[i].type == "DIV" for i in range(len(tokens))):
				# Find last operation of type MULT or DIV outside of parentheses

				in_paren = False
				for i in range(len(tokens)-1, 0, -1):
					if tokens[i].type == "RPAREN":
						in_paren = True
					elif tokens[i].type == "LPAREN":
						in_paren = False
					if (tokens[i].type == "MULT" or tokens[i].type == "DIV") and not in_paren:
						return BinOp(self.parse_math(tokens[:i]), tokens[i].value, self.parse_math(tokens[i+1:]))
			if any(tokens[i].type == "POWER" for i in range(len(tokens))):
				in_paren = False
				for i in range(len(tokens)-1, 0, -1):
					if tokens[i].type == "RPAREN":
						in_paren = True
					elif tokens[i].type == "LPAREN":
						in_paren = False
					if tokens[i].type == "POWER" and not in_paren:
						return BinOp(self.parse_math(tokens[:i]), tokens[i].value, self.parse_math(tokens[i+1:]))
			if any(tokens[i].type == "LPAREN" for i in range(len(tokens))):				
				# Find last parenthesis
				l_ind = None
				r_ind = None
				for i in range(len(tokens)-1, -1, -1):
					if tokens[i].type == "RPAREN":
						r_ind = i
					if tokens[i].type == "LPAREN":
						l_ind = i
						return self.parse_math(tokens[l_ind+1:r_ind])
			return tokens[0].value
		else:
			raise Exception(f"Invalid token {tokens[0].value} on line {tokens[0].lineno}")

	def parse_id(self):
		if self.current_token.type != 'ID': raise Exception('Expected ID')
		if not (self.next_token.type == 'ASSIGN' or self.next_token.type == 'ADD' or self.next_token.type == 'SUB'):
			raise Exception(f"Invalid token {self.next_token.value} on line {self.next_token.lineno}")
		if self.next_token.type == 'ASSIGN':
			var_name = self.current_token.value
			self.eat_token('ASSIGN') # -> current_token = ASSIGN, next_token = value
			self.get_next_token() # -> current_token = value, next_token = ?
			if self.next_token.type == 'LNEND':
				return VarStatement(var_name, self.current_token.value)
			return VarStatement(var_name, self.parse_math(self.get_line()))
		elif self.next_token.type == "ADD" or self.next_token.type == "SUB":
			add_bin = BinOp(self.current_token.value, "+" if self.next_token.type == "ADD" else '-', 1)
			varSt = VarStatement(self.current_token.value, add_bin)
			self.eat_token('ADD' if self.next_token.type == "ADD" else 'SUB')
			return varSt
			
	def parse_function(self):
		if self.current_token.type != 'DEF': raise Exception('Expected DEF')
		self.get_next_token()

		attrs = []
		print(self.current_token, self.next_token)
		# start -> attr, atrr, ..., ID
		# end -> attr, ID
		while True:
			if self.current_token.type.endswith('attr'):
				attrs.append(self.current_token.value)
				
			if self.next_token.type == 'ID': break
			self.get_next_token()

		self.eat_token('ID')
		FuncSt = FunctionDeclaration(self.current_token.value)
		for attr in attrs:
			FuncSt.add_attr(Attribute(attr))
		self.eat_token('LPAREN')
		self.get_next_token()
		print(self.current_token, self.next_token)
		print(FuncSt)
		exit()

	def parse(self):
		while True:
			if self.current_token.type == 'LNEND':
				self.get_next_token()
				continue
			if self.current_token.type == "ID":
				self.ast.main.children.append(self.parse_id())
				self.get_next_token()

			elif self.current_token.type in ['STRINGattr', 'INTattr', 'FLOATattr', 'BOOLattr', 'NULLattr']:
				attr = Attribute(self.current_token.value)
				self.get_next_token()
				rest = self.parse_id()
				if isinstance(rest, VarStatement):
					rest.add_attr(attr)
					self.ast.main.children.append(rest)
					self.get_next_token()

			elif self.current_token.type == 'DEF':
				self.ast.main.children.append(self.parse_function())
				self.get_next_token()
		
			elif self.current_token.type == "IF":
				pass

			if not self.current_token:
				break

# ===================== TESTING =====================
data = open("examples/test.ta", "r").read()
from TallyTokenizer import get_lexer, export_tokens

lexer = get_lexer()
lexer.input(data)
parser = Parser(lexer)

parser.parse()
print(parser.ast)