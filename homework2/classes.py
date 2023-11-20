import itertools
import time
from collections import defaultdict

class Apriori:

    def __init__(self, data, s):
        # dataset
        self.data = data
        # mininum support
        self.s = s
        # Set of candidate k-itemsets (potentiahy large itemsets).
        # Each member of this set has two fields: 
        # i) itemset and 
        # ii) support count.
        self.C_k = defaultdict(int)
        # Set of large k-itemsets (those with minimum support).
        # Each member of this set has two fields: 
        # i) itemset and 
        # ii) support count.
        self.L = {}

    # Fist count of the itemset
    def first_pass(self, item):
        # add one to the count of this itemset(size 1)
        self.C_k[item] += 1
        return item

    # Generate C_k -> set of candidate itemsets
    # Inputs:
    # - L = Set of large itemsets
    # - k = size
    def apriori_gen(self, L, k):
        # Extract the list of large itemsets of size k-1
        L_k = list(L.keys())

        # Initialize an empty dictionary for candidate itemsets of size k
        C_k = {}

        # Generate candidate itemsets by merging pairs of large itemsets a and b
        for a in L_k:
            for b in L_k:
                # Check if the first k-2 items are the same and the last item of b is greater
                if a[:k-2] == b[:k-2] and b[k-2] > a[k-2]:
                    # Merge the itemsets to form a new candidate of size k
                    new_candidate = a[:k-1] + (b[k-2],)
                    C_k[new_candidate] = 0  # Initialize the count for the new candidate as 0

        # Identify and remove candidates whose subsets are not all large itemsets
        for candidate in list(C_k):
            # Generate all subsets of size k-1
            subsets = list(itertools.combinations(candidate, k-1))
            # Check if any subset is not large
            if any(subset not in L for subset in subsets):
                # Remove the candidate itemset if any subset is not large
                del C_k[candidate]

        # Return the pruned set of candidate itemsets
        return C_k
        
    # Gets all subsets of t that are candidate pairs, i.e. are in Ck
    def get_subsets(self, Ck, t, k):
        subsets = []
        # Generates all possible subsets of size k
        for c in itertools.combinations(t, k):
            if c in Ck:
                subsets.append(c)
        return subsets

    def algorithm(self, verbose):
        t_k = time.time()
        basket_list = []
        with open(self.data, 'r') as f:
            for basket in f:
                # This will store the processed items for the current basket
                processed_basket = []  
                for item in basket.split():
                    # Process each item
                    processed_item = self.first_pass(int(item)) 
                    processed_basket.append(processed_item)
                basket_list.append(processed_basket)
        
        # Saves itemsets of dimension 1 (one item) that have at least support s
        self.L[1] = {}
        for item in sorted(self.C_k):
            if self.C_k[item] >= self.s:
                self.L[1][(item,)] = self.C_k[item]
        
        k = 1
        while len(self.L[k]) != 0:
            if verbose:
                print(k, "- itemset time", time.time() - t_k, "size of L_" + str(k) + "  is ", len(self.L[k]))
            t_k = time.time()
            k += 1
            
            # Generate all candidate itemsets
            C_k = self.apriori_gen(self.L[k-1], k)
            
            for t in basket_list:
                # Gets all candidate subsets itemsets contained in t
                C_t = self.get_subsets(C_k, t, k)
                for c in C_t:
                    # Increment the count for each candidate
                    if c not in C_k:
                         # Initialize if not present
                        C_k[c] = 0 
                    C_k[c] += 1
            
            # Filter out itemsets that don't have at least support s
            self.L[k] = {}
            for item in C_k:
                if C_k[item] >= self.s:
                    self.L[k][item] = C_k[item]
        
        # Remove the last empty itemset list
        self.L.pop(len(self.L))
        
        return self.L

class AssociationRules:

    def find(self, L, c, verbose):
        # Initialize an empty list to store the association rules
        rules = []
        # Loop through the list L from index 2 to the length of L
        for k in range(2, len(L)+1):
            # Iterate over each itemset (key) in the dictionary at index k of list L
            for key in L[k].keys():
                # Generate all possible combinations of the itemset with size k-1 (to get the antecedent of the rule)
                for subset in itertools.combinations(key, k-1):
                    # For each item in the original itemset (key)
                    for k1 in key:
                        # Check if the item (k1) is not in the current subset (to form the consequent of the rule)
                        if k1 not in subset:
                            # Calculate the confidence as the support of the itemset divided by the support of the antecedent
                            confidence = L[k][key] / L[k-1][subset]
                            # If the confidence is greater or equal to the threshold c
                            if c <= confidence:
                                # Add the rule with the consequent as a single item
                                rules.append([subset, k1, confidence])
        
        # If verbose is True, print each rule
        if verbose:
            for rule in rules:
                # Print the antecedent 'subset' -> the consequent 'k1'
                print(rule[0], "->", rule[1])
        
        # Return the list of association rules
        return rules