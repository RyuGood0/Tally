from TallyParser import TallyParser
from dataclasses import dataclass

def raise_error(comment):
	print(comment)
	exit()

@dataclass
class Variable:
	name: str
	type: int
	dynamic: bool = False
	constant: bool = False

@dataclass
class Function:
	name: str
	args: list
	body: list
	type: int

dynamic_type_map = {
	'int': 0,
	'float': 1,
	'str': 2,
	'bool': 3,
	'list': 4,
	'dict': 5,
	'tuple': 6,
	'set': 7,
	'any': 8
}

import uuid
class TallyTranspiler(object):
	parser = TallyParser()
	parser.build()

	variables = {} # {name: Variable}
	functions = {} # {name: Function}

	def __call__(self, content):
		parsed = self.parser.parse(content)

		code_c = ""

		for statement in parsed[1]:
			"""
			Start by defining all functions,
			then add all to main()
			"""
			
			transpiled = self.transpile(statement)
			code_c += transpiled + "\n"

		return code_c

	def clean_statements(self, statements):
		# TODO
		"""
		for fstring statements, add an assign statement ("str_UUID = ***") before the top call and a del statement after

		Ex:
		[('func_call', 'print', [('fstring', 'Hello {a}')]] -> [('assign', 'str', 'str_UUID', 'Hello {a}'), ('func_call', 'print', [('id', 'str_UUID')]), ('del', 'str_UUID')]
		[('assign', 'var_name', ('fstring', 'Hello {a}'))] -> [('assign', 'str', 'str_UUID', 'Hello {a}'), ('assign', 'var_name', ('id', 'str_UUID')), ('del', 'str_UUID')
		[('if', ['==', 1, 1.000], [('assign', 'var_name', ('fstring', 'Hello {a}'))])] -> [('if', ['==', 1, 1.000], [('assign', 'str', 'str_UUID', 'Hello {a}'), ('assign', 'var_name', ('id', 'str_UUID')), ('del', 'str_UUID')])]
		"""
		pass
	
	def is_assigned(self, var_name):
		# return True if variable is assigned, False otherwise
		if var_name in self.variables:
			return True
		return False

	def transpile(self, statement):
		if isinstance(statement, int):
			return str(statement)
		elif isinstance(statement, float):
			return str(statement)
		elif isinstance(statement, str):
			return str
		
		if statement[0] == "assign":
			if len(statement) == 3:
				"""
				("assign", "var_name", value), dynamic type

				assignement:
				dynamic_t* a = init_dynamic_var(INT, (void*)&(int){3});
				dynamic_t* b = init_dynamic_var(FLOAT, (void*)&(float){1.5});
				dynamic_t* c = init_dynamic_var(STRING, (void*)"hello");

				update:
				c = update_dynamic_var(c, FLOAT, (void*)&(float){2.5});
				"""
				if self.is_assigned(statement[1]) and self.variables[statement[1]].constant:
					raise_error(f"Cannot assign to constant variable: {statement[1]}")

				d_type = dynamic_type_map[self.get_inferred_type(statement[2])]
				right_member = self.transpile(statement[2])
				if not self.is_assigned(statement[1]):
					self.variables[statement[1]] = Variable(statement[1], d_type, True)

					if d_type == dynamic_type_map['int']:
						return f"dynamic_t* {statement[1]} = init_dynamic_var(INT, (void*)&(int){{{right_member}}});"
					elif d_type == dynamic_type_map['float']:
						return f"dynamic_t* {statement[1]} = init_dynamic_var(FLOAT, (void*)&(float){{{right_member}}});"
					elif d_type == dynamic_type_map['str']:
						return f"dynamic_t* {statement[1]} = init_dynamic_var(STRING, (void*)\"{right_member}\");"
					elif d_type == dynamic_type_map['bool']:
						return f"dynamic_t* {statement[1]} = init_dynamic_var(BOOL, (void*)&(bool){{{right_member}}});"
					else:
						return f"dynamic_t* {statement[1]} = init_dynamic_var(ANY, (void*)&({right_member}));"
				else:
					if d_type == dynamic_type_map['int']:
						return f"{statement[1]} = update_dynamic_var({statement[1]}, INT, (void*)&(int){{{right_member}}});"
					elif d_type == dynamic_type_map['float']:
						return f"{statement[1]} = update_dynamic_var({statement[1]}, FLOAT, (void*)&(float){{{right_member}}});"
					elif d_type == dynamic_type_map['str']:
						return f"{statement[1]} = update_dynamic_var({statement[1]}, STRING, (void*)\"{right_member}\");"
					elif d_type == dynamic_type_map['bool']:
						return f"{statement[1]} = update_dynamic_var({statement[1]}, BOOL, (void*)&(bool){{{right_member}}});"
					else:
						return f"{statement[1]} = update_dynamic_var({statement[1]}, ANY, (void*)&({right_member}));"
					
			else:
				"""
				('assign', 'int', 'a', 4)

				assignement:
				int a = 4;
				"""
				
				if self.is_assigned(statement[2]) and self.variables[statement[2]].constant:
					raise_error(f"Cannot assign to constant variable: {statement[2]}")

				d_type = dynamic_type_map[statement[1]]
				right_member = self.transpile(statement[3])
				if not self.is_assigned(statement[2]):
					self.variables[statement[2]] = Variable(statement[2], d_type, False)

					if d_type == dynamic_type_map['int']:
						return f"int {statement[2]} = {right_member};"
					elif d_type == dynamic_type_map['float']:
						return f"float {statement[2]} = {right_member};"
					elif d_type == dynamic_type_map['str']:
						return f"char* {statement[2]} = \"{right_member}\";"
					elif d_type == dynamic_type_map['bool']:
						return f"bool {statement[2]} = {right_member};"
					else:
						return f"void* {statement[2]} = {right_member};"
					
				else:
					raise_error(f"Variable already assigned: {statement[2]}")
		
		elif statement[0] == "fstring":
			"""
			('fstring', 'Hello {a}! Hi {b}')

			code:
			fstring("Hello %s! Hi %s", (char* []){dynamic_var_to_string(a), dynamic_var_to_string(b)})
			"""

			# get all var_names
			var_names = []
			for i in range(len(statement[1])):
				if statement[1][i] == '{' and (i == 0 or statement[1][i-1] != '\\'):
					var_name = ""
					i += 1
					while statement[1][i] != '}':
						var_name += statement[1][i]
						i += 1

					if not self.is_assigned(var_name):
						raise_error(f"Variable not assigned: {var_name}")

					var_names.append(var_name)

			# get all str conversions
			str_conversions = []
			for var_name in var_names:
				str_conversions.append(self.string_conversion(var_name))

			# create fstring call
			format_string = ""
			i = 0
			while i < len(statement[1]):
				if statement[1][i] == '{' and (i == 0 or statement[1][i-1] != '\\'):
					format_string += "%s"
					i += 1
					while statement[1][i] != '}':
						i += 1
				else:
					format_string += statement[1][i]
				i += 1

			fstring_call = f"fstring(\"{format_string}\", (char* []){{"
			for i in range(len(str_conversions)):
				fstring_call += str_conversions[i]
				if i != len(str_conversions) - 1:
					fstring_call += ", "

			fstring_call += "})"

			return fstring_call

		elif statement[0] == "func_call":
			if statement[1] == "print":
				"""
				('func_call', 'print', ['hello world', a])

				code:
				pprint(4, (char* []){copy_string("hello world"), dynamic_var_to_string(a)});
				"""
				
				# get all str conversions
				str_conversions = []
				for i in statement[2]:
					if isinstance(i, str):
						str_conversions.append(f"copy_string(\"{i}\")")
					else:
						str_conversions.append(self.string_conversion(i[1]))

				# create print call
				print_call = f"pprint({len(str_conversions)}, (char* []){{"
				for i in range(len(str_conversions)):
					print_call += str_conversions[i]
					if i != len(str_conversions) - 1:
						print_call += ", "

				print_call += "})"
				return print_call

		raise_error(f"Unknown statement type: {statement}")
		
	def string_conversion(self, var_name):
		stored_var = self.variables[var_name]

		if stored_var.dynamic:
			return f"dynamic_var_to_string({var_name})"
		elif stored_var.type == dynamic_type_map['str']:
			return f"copy_string({var_name})"
		elif stored_var.type == dynamic_type_map['int']:
			return f"int_to_string({var_name})"
		elif stored_var.type == dynamic_type_map['float']:
			return f"float_to_string({var_name})"
		elif stored_var.type == dynamic_type_map['bool']:
			return f"bool_to_string({var_name})"
		else:
			raise_error(f"Cannot convert type to string: {stored_var.type}")

	def get_inferred_type(self, statement):
		if isinstance(statement, int):
			return 'int'
		elif isinstance(statement, float):
			return 'float'
		elif isinstance(statement, str):
			return 'str'
		elif statement[0] == 'func_call':
			return self.functions[statement[1]].type
		elif statement[0] == 'fstring':
			return dynamic_type_map['str']

		return dynamic_type_map['any']

if __name__ == '__main__':
	file_path = "examples/test.ta"
	with open(file_path, 'r') as file:
		data = file.read()
		tally = TallyTranspiler()
		c_code = tally(data)

		print("Transpiled code:")
		print(c_code)

	run = True

	if run:
		with open("temp.c", "w") as f:
			f.write(c_code)

		#import subprocess
		#subprocess.Popen("gcc -o out temp.c")
		#subprocess.Popen("./out")
