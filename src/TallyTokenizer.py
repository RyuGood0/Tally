class Token():
	def __init__(self, token_type, value):
		self.type = token_type
		self.value = value
	
	def __str__(self):
		return f"Token type : {self.type} of value {self.value}"
	
	def __repr__(self):
		return f"Token type : {self.type} of value {self.value}"

from os import path
meta_path = path.realpath(__file__).rsplit('\\', 1)[0].replace('\\', '/') + "/metadata.txt"
metadatas = open(meta_path, "r")

alphas = []
in_alphas = False
symbols = []
in_symbols = False
for line in metadatas.readlines():
	if in_alphas == True:
		alphas.append(line.replace("\n", ""))
	if line == "Alpha token :\n":
		in_alphas = True
	elif line.isspace():
		in_alphas = False
	if in_symbols == True:
		symbols.append(line.replace("\n", ""))
	if line == "Symbol token :\n":
		in_symbols = True
	elif line.isspace():
		in_symbols = False

metadatas.close()

def isFloat(value):
	try:
		float(value)
		return True
	except ValueError:
		return False

def make_token(value):
	if value in alphas:
		return Token(value, value)
	elif value.isdigit():
		return Token("int", value)
	elif isFloat(value):
		return Token("float", value)
	elif value.isalnum():
		return Token("id", value)
	return Token(value, value)

def skip_spaces(text, index):
	while index < len(text) and text[index].isspace() and text[index] != "\n":
		if index == len(text)-1:
			break
		index += 1
	return index

def get_next_token(text, line_num):
	i = 0
	buffer = ""
	i = skip_spaces(text, i)
	if not (i < len(text)):
		return Token("lnend", "\\n"), text[i:], line_num
	if text[i] == "\n":
		line_num += 1
		i += 1
		return Token("lnend", "\\n"), text[i:], line_num	
	elif text[i].isalpha() or text[i] == "_":
		while i < len(text) and (text[i].isalnum() or text[i] == "_"):
			buffer += text[i]
			i += 1
	elif text[i].isdigit():
		while i < len(text) and (text[i].isdigit() or text[i] == "."):
			buffer += text[i]
			i += 1
	elif text[i] in symbols:
		if text[i] == "!" or text[i] == "<" or text[i] == ">" or text[i] == "=":
			if i != len(text)-1 and text[i+1] == "=":
				buffer = text[i:i+2]
				i += 2
			else:
				buffer = text[i]
				i += 1
		elif text[i] == "-":
			if i != len(text)-1 and text[i+1] == "=":
				buffer = text[i:i+2]
				i += 2
			elif i != len(text)-1 and text[i+1] == "-":
				buffer = text[i:i+2]
				i += 2
			else:
				buffer = text[i]
				i += 1
		elif text[i] == "+":
			if i != len(text)-1 and text[i+1] == "=":
				buffer = text[i:i+2]
				i += 2
			elif i != len(text)-1 and text[i+1] == "+":
				buffer = text[i:i+2]
				i += 2
			else:
				buffer = text[i]
				i += 1
		else:
			buffer = text[i]
			i += 1
	else:
		print(f"unknown token on line {line_num} : {text[i]}")
		exit(1)
	return make_token(buffer), text[i:], line_num

def get_all_tokens(content):
	tokens = []
	line_num = 1
	while content != "":
		token, content, line_num = get_next_token(content, line_num)
		tokens.append(token)
	
	return tokens