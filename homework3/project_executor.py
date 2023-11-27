import time
import argparse
from homework_classes import TriestBase, TriestImpr

# Create a parser object to handle command-line arguments
parser = argparse.ArgumentParser(description="Find triangles' (global or local) estimates in a graph using TRIEST.")


# Add command-line arguments to the parser
parser.add_argument('-dataset-file', default='web-Stanford.txt.gz', help='path to the dataset')
parser.add_argument('-triest', default='impr', choices=['base', 'impr'], type=str, help='TRIEST algorithm')
parser.add_argument('-M', default=10000, type=int, help='resorvoir sampling size')
parser.add_argument('-verbose', default=False, action='store_true', help='set true to print the results')

# Parse the command-line arguments and print them
args = parser.parse_args()
print(args)

# Depending on the mode selected by the user, instanciate a different Triest class
if args.triest == 'base':
    # Call Triest Base passing sampling size M and verbose flag
    triest = TriestBase(args.M, args.verbose)
else:
    # Call Triest Improved passing sampling size M and verbose flag
    triest = TriestImpr(args.M, args.verbose)

# Save the starting time and call the algorithm associated to the wanted algorithm (Base or Improved)
start_time = time.time()
global_triangles = triest.algorithm(args.dataset_file)

# Print the time requested by the algorithm
elapsed_time = time.time() - start_time
print(f'TRIEST-{args.triest.upper()} took {elapsed_time:.3f}s')