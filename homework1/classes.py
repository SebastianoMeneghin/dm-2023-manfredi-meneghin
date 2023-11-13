import math
import numpy as np
import sympy as sp
import itertools
from scipy import sparse
from collections import defaultdict


class Shingling:
    # The constructor for the class Shingling, with default shingles_len = 10
    def __init__(self, shingles_len=10):
        self.shingles_len = shingles_len

    # A shingle is hashed on a number from 0 to 2^32
    def hash_shingles(self, shingle):
        hashed_shingle = 0

        # Each character of the shingle is computed and all of their results are summed in hashed_shingle
        for char_idx, character in enumerate(shingle):
            hashed_shingle += pow(100, char_idx) * ord(character)

        # The modulo of hashed_shingles is calculated, in order to hash the sum
        hashed_shingle = hashed_shingle % (2**32)
        return hashed_shingle
    
    # The essay text is divided in shingles of the same length. Each of them is then hashed
    # All the values are sorted and duplicates are removed
    def create_unique_shingles(self, essay):
        unique_shingles = []

        # The essay is divided in small shingles
        for i in range(len(essay) - self.shingles_len + 1):
            shingle = essay[i:(i + self.shingles_len)]
            hash_value = self.hash_shingles(shingle)

            # If not already present, the shingles is added to the set
            if hash_value not in unique_shingles:
                unique_shingles.append(hash_value)

        # Finally, shingles' set is sorted
        unique_shingles.sort()
        return unique_shingles

    # For each essay, creates its shingles' set. Then it creates a global dictionary (idx, shingles)
    def create_essay_shingles(self, essay_list):
        essay_shingles = []

        # For each essay, the respective shingles' set is created
        for essay in essay_list:
            single_shingle = self.create_unique_shingles(essay)
            essay_shingles.append(single_shingle)
            
        # A global set of shingles is created
        global_shingles = set()
        for shingles in essay_shingles:
            global_shingles.update(shingles)

        # A dictionary (shingleIdx, shingle) is created
        shingle_idxs = {}
        for idx, shingle in enumerate(global_shingles):
            shingle_idxs[shingle] = idx

        return essay_shingles, shingle_idxs

    # Create a characteristic matrix from the global shingles dictionary and each essays' shingles list
    def create_characteristic_matrix(self, essay_list):

        # After calling the functions, get the number of essays and the number of global shingles
        essay_shingles, shingle_idxs = self.create_essay_shingles(essay_list)
        n_essays, n_shingles = len(essay_shingles), len(shingle_idxs)

        # For each essay' shingles list, it gets each shingle and aggregates in a tuple its id, essay_idx to which it
        # belongs and a value "1". Then the list of tuples is transposed three lists.
        vals = []
        for essay_idx, shingles in enumerate(essay_shingles):
            for shingle in shingles:
                shingle_index = shingle_idxs[shingle]
                vals.append((shingle_index, essay_idx, 1))

        shingle_indices, essay_indices, data = zip(*vals)

        # Creates a sparse matrix from the lists created above. Data contains all the ones.
        # The matrix is shaped with the global number of shingles for the rows and with the number of essays for the columns
        characteristic_matrix = sparse.csr_matrix((data, (shingle_indices, essay_indices)), shape=(n_shingles, n_essays), dtype=np.bool_)
        # In case its not relevant having "True" or "False"
        #characteristic_matrix = sparse.csr_matrix((data, (shingle_indices, essay_indices)), shape=(n_shingles, n_essays))
        
        return characteristic_matrix


class CompareSets:

    # The Jaccard similirity is computed, dividing the sets intersection's size by the sets union's size
    @staticmethod
    def jaccard_similarity(set_1, set_2):
        set_1, set_2 = set(set_1), set(set_2)
        similarity = len(set_1.intersection(set_2)) / len(set_1.union(set_2))
        return similarity


class MinHashing:

    def __init__(self, sign_number=500):
        self.sign_number = sign_number

    def compute_signature_hash(self, characteristic_matrix):
        # Get the sign_number and the size of the characteristic matrix
        sign_number = self.sign_number
        n_shingles, n_essay = characteristic_matrix.shape

        # Initialize each cell of the signature matrix with +infinity
        signature = np.full((sign_number, n_essay), np.inf)

        # Choose p as the first prime number after the total number of shingles
        p = sp.nextprime(n_shingles)

        # Choose two vectors of sign_number random values between 0 and p, the total number of shingles.
        a = 2 * np.random.randint(0, p//2, sign_number) + 1
        b = np.random.randint(0, p, sign_number)

        # Iterate now over the rows of the characteristic_matrix (each rows represent a global shingle)
        for row_idx, essay_idxs in enumerate(characteristic_matrix.tolil().rows):

            # Compute sign_number independent hash functions for each row_idx
            hashes = self.compute_universal_hash(row_idx, a, b, p, n_shingles)

            # Iterate over the essays which contain that shingle
            for essay_idx in essay_idxs:
                # Select the column representing the current essay
                current_column = signature[:, essay_idx]

                # Iterate over the results given by the different hash functions on the same row_idx
                for hash_fun_res in range(sign_number):
                    # Update the signature matrix if the result of the specific hash function is less than the current value (the matrix have been set to +infinite)
                    if hashes[hash_fun_res] < current_column[hash_fun_res]:
                        signature[hash_fun_res, essay_idx] = hashes[hash_fun_res]
        
        return signature
    
    # Computes as many hash function as the length of the the arrays "a" and "b", so as many as sign_num
    # Parameters are choosen according to Corman et al., Introduction to Algorithms, ISBN: 9780262530910
    def compute_universal_hash(self, x, a, b, p, m):
        return ((a*x + b) % p) % m


class CompareSignatures:
   
    @staticmethod
    def signature_similarity(signature, essay_1, essay_2):
        # Get the MinHash signatures for the two essays
        signature_1 = signature[:, essay_1]
        signature_2 = signature[:, essay_2]

        # Count the number of equal elements
        equal_elements = np.sum(signature_1 == signature_2)

        # Calculate the total number of elements
        total_elements = len(signature_1)

        # Return the similarity fraction
        return equal_elements / total_elements


class LSH:

    def __init__(self, band_number=100, threshold=0.8):
        self.band_number = band_number
        self.threshold = threshold

    def find_candidates_pairs(self, signature):
        # Get signature matrix size
        band_number = self.band_number
        sign_number = signature.shape[0]

        # Determine the rows size
        rows_band = math.ceil(sign_number / band_number)

        candidate_pairs = set()
        column_buckets = defaultdict(list)

        # Then divide the signature matrix in band_number bands, and for each:
        for band_idx in range(band_number):

            # Get the chunk of rows which correspond to a band
            band_head = band_idx*rows_band
            band_tail = (band_idx+1)*rows_band
            band = signature[band_head: band_tail]

            # Transpose the band to be able to save them as key and iterate over its columns (so over the essays)
            for essay_idx, column in enumerate(band.T):
                # Values in the column are converted into a tuple, so we can use it as a key that is hashable
                dic_key = tuple(column)

                # Then we store all documents in this band with identical key (hashes)
                column_buckets[dic_key].append(essay_idx)

            # Then, for each bucket, it creates all the possible couple combinations between elements belonging to the same bucket.
            for essay_idxs in column_buckets.values():
                pairwise_combinations = itertools.combinations(essay_idxs, 2)
                candidate_pairs.update(pairwise_combinations)

            # Clear the buckets, since each band should be hashed in independent buckets
            column_buckets.clear()

        return candidate_pairs
    
    def find_similar_pairs(self, signature):
        # Find the candidate pairs by applying LSH algorithm
        candidate_pairs = self.find_candidates_pairs(signature)
        similar_essays = []

        # Select only the candidate pairs that have a similiraty higher then the defined threshold
        for candidate_pair in candidate_pairs:
            essay_1 = candidate_pair[0]
            essay_2 = candidate_pair[1]
            essay_similarity = CompareSignatures.signature_similarity(signature, essay_1, essay_2)

            if essay_similarity > self.threshold:
                similar_essays.append(candidate_pair)

        return similar_essays