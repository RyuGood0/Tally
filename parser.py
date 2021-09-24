import tokenizer
class AST:
	def __init__(self):
		self.nodes = []

	def __repr__(self):
		buffer = ""
		for node in self.nodes:
			buffer += f"Parent node {node} of child {node.children}\n"
		return buffer
	
	def __str__(self):
		buffer = ""
		for node in self.nodes:
			buffer += f"Parent node {node} of child {node.children}\n"
		return buffer
	
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

def token_error(token, expected_type, line_num):
	print(f"line {line_num} : got token {token.type}, expected {expected_type}")
	exit(1)

def expect_token(expected_types, content, line_num):
	token, content, line_num = tokenizer.get_next_token(content, line_num)
	if token.type in expected_types:
		return tokenizer.get_next_token(content, line_num)
	else:
		token_error(token, expected_types, line_num)

def skip_comment(token, content, line_num):
	if token.type == "#":
		while token.type != "lnend":
			token, content, line_num = tokenizer.get_next_token(content, line_num)
	
	return token, content, line_num

def parse_token(ast, token, content, line_num):
	token, content, line_num = skip_comment(token, content, line_num)
	raise NotImplementedError()
	return ast, token, content, line_num

def parse_function(ast, token, content, line_num):
	def_node = Node(None, token)
	token, content, line_num = tokenizer.get_next_token(content, line_num)
	if token.type == "int" or token.type == "str" or token.type == "float" or token.type == "bool":
		def_node.modifiers.append(Node(def_node, token))
		token, content, line_num = tokenizer.get_next_token(content, line_num)
		if token.type == "id":
			def_node.modifiers.append(["name", Node(def_node, token)])
		else:
			token_error(token, "id", line_num)
	elif token.type == "id":
		def_node.modifiers.append(["name", Node(def_node, token)])
		token, content, line_num = tokenizer.get_next_token(content, line_num)
	else:
		print(f"unexpected token {token.value} after def")

	token, content, line_num = expect_token(["("], content, line_num)
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
			token, content, line_num = expect_token([",", ")"], content, line_num)
		elif token.type == "int" or token.type == "float" or token.type == "str" or token.type == "bool":
			arg_type = token
			token, content, line_num = expect_token([":"], content, line_num)
		else:
			break
	
	if token.type != "{":
		token_error(token, "{", line_num)

	while token.type != "}":
		ast, token, content, line_num = parse_token(ast, token, content, line_num)

	ast.nodes.append(def_node)
	return ast, token, content, line_num

def build_ast(content):
	ast = AST()
	line_num = 1
	while content != "":
		token, content, line_num = tokenizer.get_next_token(content, line_num)
		if token.type == "def":
			ast, token, content, line_num = parse_function(ast, token, content, line_num)
			
	return ast

def read_ast():
	# TODO
	pass
