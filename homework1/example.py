from data_extractor import extract_data
from data_processor import DataProcessor
from classes import Shingling, CompareSets, MinHashing, CompareSignatures, LSH

# Extract the dataset of essays and select 100 essays
essays = extract_data('persuade_2.0_.zip', 100)

# Instanciate and initialize DataProcessor, Shinglinh, MinHashin and LSH with some specific default values (more in "project_executor")
dataprocessor = DataProcessor()
shingling = Shingling(10)
min_hashing = MinHashing(500)
lsh = LSH(100)

# Test on only two different essays
essay_23 = shingling.create_unique_shingles(essays[22])
essay_25 = shingling.create_unique_shingles(essays[24])
print('\n################## SIMILARITY BETWEEN TWO ESSAYS ##################')
print(f'The similarity between the two essays is: {CompareSets.jaccard_similarity(essay_23, essay_25)} \n')

# Test instead five different essays
essays_idxs = [5, 27, 38, 63, 89]
essays_list = []
for essay_idx in essays_idxs:
    essays_list.append(essays[essay_idx])

# The data are processed and the characteristic matrix is calcuted on the normalized and corrected data
processed_essays = dataprocessor.process_essays(essays_list)
characteristic_matrix = shingling.create_characteristic_matrix(processed_essays)


print('################## SIGN SIMILARITY BETWEEN FIVE ESSAYS ##################')
# The signature comparison between the set documents is done
signature_hash = min_hashing.compute_signature_hash(characteristic_matrix)
for essay_1 in range(len(essays_idxs)):
    for essay_2 in range(essay_1+1, len(essays_idxs)):
        # For each pair of documents, compute and print the similarity of their signature:
        similarity = CompareSignatures.signature_similarity(signature_hash, essay_1, essay_2)
        print(f'The similarity between the signature of essay {essay_1 + 1} and essay {essay_2 + 1} is: {similarity}')

print('\n\n################## SIMILAR PAIRS ##################')
similar_documents = lsh.find_similar_pairs(signature_hash)
print(f'Couples of similar document are: {similar_documents}\n')