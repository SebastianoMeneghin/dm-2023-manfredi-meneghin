import time
import argparse
from classes import Apriori, AssociationRules

# Create a parser object to handle command-line arguments
parser = argparse.ArgumentParser(description='Find frequent itemsets and association rules for a given support/confidence')

# Add command-line arguments to the parser
parser.add_argument('-dataset-file', default='homework2/datasets/T10I4D100K.dat', help='name of a transactions dataset with baskets and items')
parser.add_argument('-s', default=1000, type=int, help='minimum support a itemset must have to be considered frequent')
parser.add_argument('-c', default=0.5, type=float, help='minimum confidence a rule must have to be generated')
parser.add_argument('-verbose', default=True, type=bool, help='decides if the results are printed')

# Parse the command-line arguments
args = parser.parse_args()

# Print the parsed arguments
print(args)

# Get the current time
t = time.time()

# Create an Apriori object with the given dataset file and minimum support
apriori = Apriori(datasets=args.dataset_file, s=args.s)

# Run the Apriori algorithm and get the frequent itemsets
L_k = apriori.algorithm(verbose=args.verbose)

# If verbose is True, print the time taken for the first sub problem
if args.verbose:
    print("time for sub problem 1", time.time() - t )

# Get the current time
t = time.time()

# Create an AssociationRules object
associationrules = AssociationRules()

# Find the association rules with the given frequent itemsets and minimum confidence
rules = associationrules.find(L_k, c=args.c, verbose=args.verbose)

# If verbose is True, print the time taken for the second sub problem
if args.verbose:
    print("time for sub problem 2",time.time()-t)