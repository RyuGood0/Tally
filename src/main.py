from TallyTranspiler import TallyTranspiler

# parse command line arguments
import argparse
parser = argparse.ArgumentParser(description='Transpile Tally code.')
parser.add_argument('input', metavar='input', type=str, nargs=1, help='input file')
parser.add_argument('-o', '--output', metavar='output', type=str, nargs=1, help='output file')
args = parser.parse_args()

# read input file
input_file = args.input[0]
with open(input_file, 'r') as f:
    input_code = f.read()

# transpile
transpiler = TallyTranspiler()
output_code = transpiler(input_code)

# get backend
backend_file = 'src/backend.c'
with open(backend_file, 'r') as f:
    backend_code = f.read()

# write output file
if args.output:
    output_file = args.output[0]
    with open(output_file, 'w') as f:
        f.write(backend_code)
        f.write(output_code)