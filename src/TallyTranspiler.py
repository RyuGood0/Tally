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

		function_codes = []

		main_code = ""
		for statement in self.clean_statements(parsed[1]):
			"""
			Start by defining all functions,
			then add all to main()
			"""
			
			transpiled = self.transpile(statement)
			main_code += transpiled + "\n"

		code_c = ""
		for function_code in function_codes:
			code_c += function_code + "\n"

		main_code = "".join([f"\t{code}\n" for code in main_code.splitlines()])
		code_c += f"int main(int argc, char *argv[]) {{\n{main_code}"

		# add free statements for all variables
		for var_name in self.variables:
			if self.variables[var_name].dynamic:
				code_c += f"\tfree_dynamic_var(&{var_name});\n"
			else:
				code_c += f"\tfree({var_name});\n"

		code_c += "\treturn 0;\n"
		code_c += "}"

		return code_c

	def clean_statements(self, statements, assigned_vars={}):
		"""
		for fstring statements, add an assign statement ("str_UUID = ***") before the top call and a del statement after

		Ex:
		[('func_call', 'print', [('fstring', 'Hello {a}')]] -> [('assign', 'str', 'str_UUID', ('fstring', 'Hello {a}')), ('func_call', 'print', [('id', 'str_UUID')]), ('del', 'str_UUID')]
		[('assign', 'var_name', ('fstring', 'Hello {a}'))] -> [('assign', 'str', 'str_UUID', ('fstring', 'Hello {a}')), ('assign', 'var_name', ('id', 'str_UUID')), ('del', 'str_UUID')
		[('assign', 'str', 'var_name', ('fstring', 'Hello {a}'))] -> [('assign', 'str', 'var_name', ('fstring', 'Hello {a}'))]
		[('if', ['==', 1, 1.000], [('assign', 'var_name', ('fstring', 'Hello {a}'))])] -> [('if', ['==', 1, 1.000], [('assign', 'str', 'str_UUID', ('fstring', 'Hello {a}')), ('assign', 'var_name', ('id', 'str_UUID')), ('del', 'str_UUID')])]
		
		If the statement is not a fstring and does not contain a fstring, return the statement
		Else, if statement is a fstring, add assign and del statements before and after
		Else, if statement contains a fstring, check type of statement and add assign and del statements in the correct place
		=> for a func_call it should happen before the statement, but for a statement that create a new "block" (if, while, for, func_decl, ...) it should happen inside the block
		BUT for a typed assign statement, nothing should be added
		"""
		new_statements = []

		for stmt in statements:
			if not isinstance(stmt, tuple):
				new_statements.append(stmt)
				continue

			stmt_type, *stmt_data = stmt
			if stmt_type == 'assign':
				if len(stmt_data) == 3:
					var_type, var_name, var_value = stmt_data
					if var_type == 'str' and isinstance(var_value, tuple) and var_value[0] == 'fstring':
						new_statements.append((stmt_type, *stmt_data))

					assigned_vars[var_name] = Variable(var_name, dynamic_type_map[var_type])				
				else:
					# Assignment without var_type, add assign and del statements
					var_name, var_value = stmt_data
					if isinstance(var_value, tuple) and var_value[0] == 'fstring':
						str_UUID = f'str_UUID_{uuid.uuid4().hex}'  # Generate a unique str_UUID
						new_statements.append(('assign', 'str', str_UUID, ('fstring', var_value[1])))
						new_statements.append(('assign', var_name, ('id', str_UUID)))
						new_statements.append(('del', str_UUID))

						assigned_vars[var_name] = Variable(var_name, dynamic_type_map['str'], True)
					else:
						new_statements.append((stmt_type, *stmt_data))

						assigned_vars[var_name] = Variable(var_name, self.get_inferred_type(var_value), True)

			elif stmt_type == 'fstring':
				# This is an fstring, but not part of a func_call, so just add it as is
				new_statements.append((stmt_type, stmt_data[0]))

			elif stmt_type == 'func_call':
				args = []
				for arg in stmt_data[1]:
					if not isinstance(arg, tuple):
						args.append(arg)
					else:
						arg_type, *arg_data = arg
						if arg_type == 'fstring':
							# Add an assign statement before the fstring argument
							str_UUID = f'str_UUID_{uuid.uuid4().hex}'  # Generate a unique str_UUID
							new_statements.append(('assign', 'str', str_UUID, ('fstring', arg_data[0])))
							# Add the fstring argument as an id to the argument list
							args.append(('id', str_UUID))
						else:
							args.append((arg_type, *arg_data))

				# Add the func_call statement with modified arguments
				new_statements.append(('func_call', stmt_data[0], args))
				# Add a del statement for the str_UUIDs used in the fstring arguments
				for arg_type, *arg_data in stmt_data[1]:
					if arg_type == 'fstring':
						new_statements.append(('del', str_UUID))
			
			else:
				new_statements.append((stmt_type, *stmt_data))

		return new_statements

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
			return f'"{statement}"'
		
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

				d_type = self.get_inferred_type(statement[2])
				right_member = self.transpile(statement[2])
				if not self.is_assigned(statement[1]):
					self.variables[statement[1]] = Variable(statement[1], d_type, True)

					if d_type == dynamic_type_map['int']:
						return f"dynamic_t* {statement[1]} = init_dynamic_var(INT, (void*)&(int){{{right_member}}});"
					elif d_type == dynamic_type_map['float']:
						return f"dynamic_t* {statement[1]} = init_dynamic_var(FLOAT, (void*)&(float){{{right_member}}});"
					elif d_type == dynamic_type_map['str']:
						return f"dynamic_t* {statement[1]} = init_dynamic_var(STRING, (void*){right_member});"
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
						return f"{statement[1]} = update_dynamic_var({statement[1]}, STRING, (void*){right_member});"
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
						return f"char* {statement[2]} = {right_member};"
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
				('func_call', 'print', [('func_call', 'hello', []]) => hello is a function that returns a string
				('func_call', 'print', [('func_call', 'hello', [])]) => hello is a function that returns a dynamic var
				('func_call', 'print', ["Hello world!"]) => hello is a string

				code:
				pprint(4, (char* []){copy_string("hello world"), dynamic_var_to_string(a)});
				pprint(1, (char* []){hello()});
				pprint(1, (char* []){dynamic_var_to_string(hello())});
				printf("Hello world!\n");
				"""
				
				# if only one argument and it is a string, use printf
				if len(statement[2]) == 1 and isinstance(statement[2][0], str):
					return f'printf("{statement[2][0]}\\n");'

				# get all str conversions
				str_conversions = []
				for i in statement[2]:
					# parse each argument
					if isinstance(i, int):
						str_conversions.append(f"int_to_string({i})")
					elif isinstance(i, float):
						str_conversions.append(f"float_to_string({i})")
					elif isinstance(i, str):
						str_conversions.append(f'copy_string("{i}")')
					elif i[0] == 'func_call':
						# check if function returns a dynamic var
						if self.functions[i[1]].type == dynamic_type_map['any']:
							str_conversions.append(self.string_conversion(i[1]))
						else:
							str_conversions.append(f"copy_string({i[1]})")
					elif i[0] == 'id':
						# check if variable is dynamic
						if self.variables[i[1]].dynamic:
							str_conversions.append(self.string_conversion(i[1]))
						else:
							str_conversions.append(f"copy_string({i[1]})")
					else:
						raise_error(f"Unknown argument type: {i}")

				# create print call
				print_call = f"pprint({len(str_conversions)}, (char* []){{"
				for i in range(len(str_conversions)):
					print_call += str_conversions[i]
					if i != len(str_conversions) - 1:
						print_call += ", "

				print_call += "});"
				return print_call

		elif statement[0] == "del":
			# free variable
			if not self.is_assigned(statement[1]):
				raise_error(f"Variable not assigned: {statement[1]}")

			if self.variables[statement[1]].dynamic:
				self.variables.pop(statement[1])
				return f"free_dynamic_var(&{statement[1]});"
			else:
				self.variables.pop(statement[1])
				return f"free({statement[1]});"

		elif statement[0] == 'id':
			return statement[1]

		elif statement[0] == 'if':
			"""
			('if', ('==', ('id', 'a'), 5), [('func_call', 'print', ['a is 5'])]) => a is a dynamic var
			('if', ('>', ('id', 'a'), ('id', 'b')), [('func_call', 'print', ['a is greater than b'])]) => a and b are a dynamic var
			('if', ('==', ('id', 'a'), 5), [('func_call', 'print', ['a is 5'])]) => a is an int
			('if', ('id', 'a'), [('func_call', 'print', ['a is 5'])]) => a is a dynamic var, or could be the result of a function that returns a dynamic var

			code:
			if (a->value == 5) {
				printf("a is 5\n");
			}

			if (dynamic_greater_than(a, b)) {
				printf("a is greater than b\n");
			}

			if (a == 5) {
				printf("a is 5\n");
			}

			if (dynamic_var_to_bool(a)) {
				printf("a is 5\n");
			}

			possibilities:
			- plain value : 5, 3.14, "hello", True, False, None, 5 + 6,...
			- variable : dynamic var or not
			- function call : dynamic or not
			"""
			
			condition = statement[1]

			condition_code = ""
			
			if isinstance(condition, tuple):
				if condition[0] == "id":
					if self.variables[condition[1]].dynamic:
						condition_code = f"dynamic_var_to_bool({condition[1]})"
					elif self.variables[condition[1]].type == dynamic_type_map['int']:
						condition_code = f"({condition[1]} == 0 ? 0 : 1)"
					elif self.variables[condition[1]].type == dynamic_type_map['float']:
						condition_code = f"({condition[1]} == 0.0 ? 0 : 1)"
					else:
						raise_error(f"Cannot convert type to bool: {self.variables[condition[1]].type}")

				elif condition[0] == "func_call":
					if self.functions[condition[1]].type == dynamic_type_map['any']:
						condition_code = f"dynamic_var_to_bool({condition[1]})"
					elif self.functions[condition[1]].type == dynamic_type_map['bool']:
						condition_code = f"{self.transpile(condition)}"
					elif self.functions[condition[1]].type == dynamic_type_map['int']:
						condition_code = f"({self.transpile(condition)} == 0 ? 0 : 1)"
					elif self.functions[condition[1]].type == dynamic_type_map['float']:
						condition_code = f"({self.transpile(condition)} == 0.0 ? 0 : 1)"

				elif condition[0] == "==":
					"""
					If both are dynamic, use dynamic_equal
					If one is dynamic and other is plain value, compare to value of dynamic var (or raise error if invalid type comparison)
					If both are plain values, compare values
					Plain values could be straight values or typed variables
					"""
					if (isinstance(condition[1], tuple) and condition[1][0] == 'id') and (isinstance(condition[2], tuple) and condition[2][0] == 'id'):
						if self.variables[condition[1][1]].dynamic and self.variables[condition[2][1]].dynamic:
							condition_code = f"dynamic_equal({condition[1][1]}, {condition[2][1]})"

						elif self.variables[condition[1][1]].dynamic and not self.variables[condition[2][1]].dynamic:
							if self.variables[condition[1][1]].type in [dynamic_type_map['int'], dynamic_type_map['float'], dynamic_type_map['bool']] and self.variables[condition[2][1]].type in [dynamic_type_map['int'], dynamic_type_map['float'], dynamic_type_map['bool']]:
								condition_code = f"({condition[1][1]}->value == {condition[2][1]})"
							elif self.variables[condition[1][1]].type == dynamic_type_map['str'] and self.variables[condition[2][1]].type == dynamic_type_map['str']:
								condition_code = f"(strcmp({condition[1][1]}->value, {condition[2][1]}) == 0)"
							elif self.variables[condition[1][1]].type == dynamic_type_map['str'] and self.variables[condition[2][1]].type in [dynamic_type_map['int'], dynamic_type_map['float']]:
								if self.variables[condition[2][1]].type == dynamic_type_map['int']:
									condition_code = f"(equals_int_string({condition[1][1]}->value, {condition[2][1]}))"
								else:
									condition_code = f"(equals_float_string({condition[1][1]}->value, {condition[2][1]}))"
							elif self.variables[condition[1][1]].type in [dynamic_type_map['int'], dynamic_type_map['float']] and self.variables[condition[2][1]].type == dynamic_type_map['str']:
								if self.variables[condition[1][1]].type == dynamic_type_map['int']:
									condition_code = f"(equals_int_string({condition[2][1]}, {condition[1][1]}->value))"
								else:
									condition_code = f"(equals_float_string({condition[2][1]}, {condition[1][1]}->value))"
							else:
								raise_error(f"Cannot compare types: {self.variables[condition[1][1]].type} and {self.variables[condition[2][1]].type}")

						else:
							if self.variables[condition[2][1]].type in [dynamic_type_map['int'], dynamic_type_map['float'], dynamic_type_map['bool']] and self.variables[condition[1][1]].type in [dynamic_type_map['int'], dynamic_type_map['float'], dynamic_type_map['bool']]:
								condition_code = f"({condition[2][1]}->value == {condition[1][1]})"
							elif self.variables[condition[2][1]].type == dynamic_type_map['str'] and self.variables[condition[1][1]].type == dynamic_type_map['str']:
								condition_code = f"(strcmp({condition[2][1]}->value, {condition[1][1]}) == 0)"
							elif self.variables[condition[2][1]].type == dynamic_type_map['str'] and self.variables[condition[1][1]].type in [dynamic_type_map['int'], dynamic_type_map['float']]:
								if self.variables[condition[1][1]].type == dynamic_type_map['int']:
									condition_code = f"(equals_int_string({condition[2][1]}->value, {condition[1][1]}))"
								else:
									condition_code = f"(equals_float_string({condition[2][1]}->value, {condition[1][1]}))"
							elif self.variables[condition[2][1]].type in [dynamic_type_map['int'], dynamic_type_map['float']] and self.variables[condition[1][1]].type == dynamic_type_map['str']:
								if self.variables[condition[2][1]].type == dynamic_type_map['int']:
									condition_code = f"(equals_int_string({condition[1][1]}, {condition[2][1]}->value))"
								else:
									condition_code = f"(equals_float_string({condition[1][1]}, {condition[2][1]}->value))"
							else:
								raise_error(f"Cannot compare types: {self.variables[condition[2][1]].type} and {self.variables[condition[1][1]].type}")

					elif (isinstance(condition[1], tuple) and condition[1][0] == 'id') or (isinstance(condition[2], tuple) and condition[2][0] == 'id'):
						id_cond = condition[1] if isinstance(condition[1], tuple) and condition[1][0] == 'id' else condition[2]
						other_cond = condition[1] if isinstance(condition[1], tuple) and condition[1][0] != 'id' else condition[2]

						# TODO

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
			return dynamic_type_map['int']
		elif isinstance(statement, float):
			return dynamic_type_map['float']
		elif isinstance(statement, str):
			return dynamic_type_map['str']
		elif statement[0] == 'func_call':
			return self.functions[statement[1]].type
		elif statement[0] == 'fstring':
			return dynamic_type_map['str']
		elif statement[0] == 'id':
			return self.variables[statement[1]].type

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
