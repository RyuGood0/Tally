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

backend_header = 'src/backend.h'
with open(backend_header, 'r') as f:
    backend_header = f.read()

# write output file
if args.output:
    output_file = args.output[0]
    with open(output_file, 'w') as f:
        f.write(backend_code)
        f.write(output_code)
else:
    # save to cache dir and compile, then run
    import os
    import subprocess
    import tempfile
    cache_dir = os.path.join(tempfile.gettempdir(), 'tally')
    os.makedirs(cache_dir, exist_ok=True)

    # write to cache file
    cache_file = os.path.join(cache_dir, 'cache.c')
    with open(cache_file, 'w') as f:
        f.write(backend_code)
        f.write(output_code)

    # add header to cache dir if it doesn't exist
    cache_header = os.path.join(cache_dir, 'backend.h')
    if not os.path.exists(cache_header):
        with open(cache_header, 'w') as f:
            f.write(backend_header)

    # compile
    cache_out = os.path.join(cache_dir, 'cache')
    subprocess.run(['gcc', '-o', cache_out, cache_file])

    # run
    subprocess.run([os.path.join(cache_dir, 'cache')])

    # clean up
    os.remove(cache_file)
    os.remove(cache_header)
    os.remove(os.path.join(cache_dir, 'cache'))