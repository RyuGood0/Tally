from TallyTokenizer import get_next_token, alphas, symbols

text = ""
line_num = 0

class AST:
	def __init__(self):
		self.nodes = []

	def __repr__(self):
		buffer = ""
		for node in self.nodes:
			buffer += f"Parent node {node}\n"
		return buffer
	
	def rebranch(self, sub_ast, parent_node):
		for node in sub_ast.nodes:
			parent_node.children.append(node)
			node.parent = parent_node
	
class Node:
	def __init__(self, parent, token):
		self.parent = parent
		self.token = token
		self.children = []
		self.modifiers = []
	
	def __repr__(self):
		buffer = f"Token [{self.token.type}]"
		if len(self.modifiers) != 0:
			buffer += f" with modifier {self.modifiers}"
		if len(self.children) != 0:
			buffer += f" and children {self.children}"
		return buffer

def token_error(token, expected_type):
	global line_num
	print(f"line {line_num} : got token {token.type}, expected {expected_type}")
	exit(1)

def eat_token(expected_types):
	global text
	global line_num
	token, text, line_num = get_next_token(text, line_num)
	if token.type in expected_types:
		token, text, line_num = get_next_token(text, line_num)
		return token
	else:
		token_error(token, expected_types)

def skip_comment(token):
	global text
	global line_num
	if token.type == "#" or token.type == "lnend":
		while token.type != "lnend":
			token, text, line_num = get_next_token(text, line_num)
		token, text, line_num = get_next_token(text, line_num)
	return token

def parse_token(ast, token):
	global text
	global line_num
	token = skip_comment(token)
	if token.type == "def":
		parse_function(ast, token)	
	elif token.type == "id":
		parse_id(ast, token, None)
		token, text, line_num = get_next_token(text, line_num)
	elif token.type == "int" or token.type == "float" or token.type == "str" or token.type == "bool":
		modifier = token
		token, text, line_num = get_next_token(text, line_num)
		parse_id(ast, token, modifier)
		token, text, line_num = get_next_token(text, line_num)
	elif token.type in alphas:
		parse_alphas(ast, token)
		token, text, line_num = get_next_token(text, line_num)
	else:
		raise ValueError(f"Unexpected token : {token}")

	return token

def parse_id(ast, token, modifier):
	global text
	global line_num
	id_token = token
	id_node = Node(None, id_token)
	if modifier != None:
		id_node.modifiers.append(modifier)
	token, text, line_num = get_next_token(text, line_num)
	if token.type == "=":
		pass
	elif token.type == "(":
		pass
	elif token.type == ".":
		pass
	elif token.type in ["+", "-", "/", "*"]:
		parse_equation(ast, id_token, token)
	else:
		raise ValueError(f"Unexpected token : {token}")

	ast.nodes.append(id_node)

def parse_equation(ast, id_token, token):
	global text
	global line_num
	equation_tokens = [id_token, token]
	while token.type != "lnend":
		token, text, line_num = get_next_token(text, line_num)
		equation_tokens.append(token)
	
	print(equation_tokens)

def parse_alphas(ast, token):
	alphas_node = Node(None, token)
	ast.nodes.append(alphas_node)

def parse_function(ast, token):
	global text
	global line_num
	def_node = Node(None, token)
	token, text, line_num = get_next_token(text, line_num)
	if token.type == "int" or token.type == "str" or token.type == "float" or token.type == "bool":
		def_node.modifiers.append(["type", Node(def_node, token)])
		token, text, line_num = get_next_token(text, line_num)
		if token.type == "id":
			def_node.modifiers.append(["name", Node(def_node, token)])
		else:
			token_error(token, "id")
	elif token.type == "id":
		def_node.modifiers.append(["name", Node(def_node, token)])
		token, text, line_num = get_next_token(text, line_num)
	else:
		print(f"unexpected token {token.value} after def")
		exit(1)

	token = eat_token(["("])
	arg_type = None
	while True:
		if token.type == "id":
			if arg_type != None:
				node = Node(def_node, token)
				node.modifiers.append(Node(node, arg_type))
				def_node.modifiers.append(["arg", node])
				arg_type = None
			else:
				def_node.modifiers.append(["arg", Node(def_node, token)])
			token = eat_token([",", ")"])
		elif token.type == "int" or token.type == "float" or token.type == "str" or token.type == "bool":
			arg_type = token
			token, text, line_num = get_next_token(text, line_num)
		else:
			break
	
	if token.type != "{":
		token = eat_token(token, "{")
	else:
		token, text, line_num = get_next_token(text, line_num)

	while token.type != "}":
		sub_ast = AST()
		token = parse_token(sub_ast, token)
		ast.rebranch(sub_ast, def_node)

	ast.nodes.append(def_node)

def build_ast(content):
	global text
	global line_num
	text = content
	line_num = 1
	ast = AST()
	token, text, line_num = get_next_token(text, line_num)
	while text != "":
		token = parse_token(ast, token)
			
	return ast
