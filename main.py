from parser import build_ast
import sys
import parser, tokenizer

if len(sys.argv) < 2:
    print('no arguments given! use "tally [code.ta] [optional_args]"')
elif sys.argv[1][-2:] != "ta":
    print("unsupported file type!")
else:
    file_name = sys.argv[1]
    file = open(file_name, "r")
    content = file.read()

    ast = parser.build_ast(content)
    print(ast)
    
    if "-t" in sys.argv:
        with open(f"{file_name[:-3]}_tokens.tat", "w") as f:
            tokens = tokenizer.get_all_tokens(content)
            for token in tokens:
                f.write(f"{token}\n")