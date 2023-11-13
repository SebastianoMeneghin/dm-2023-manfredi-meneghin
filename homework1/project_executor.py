import sys
import getopt
from data_extractor import extract_data
from data_processor import DataProcessor
from classes import Shingling, MinHashing, LSH

#Before: essay_number = 100, shingles_len = 10, sign_number = 100, band_number = 20, threshold = 0.8
# Here the default values are set.
dataset_file = 'persuade_2.0_.zip'
essay_number = 100
shingles_len = 10
sign_number = 100
band_number = 20
threshold = 0.8

# The user could insert their own values. If there's any error during the execution, the reason is displayed (except code)
try:
    opts, _ = getopt.getopt(sys.argv[1:], "h", [
        "dataset-file=",
        "essay-number=",
        "shingles-len=",
        "sign-number=",
        "band-number=",
        "threshold="
    ])
except getopt.GetoptError:
    print("Usage: script.py --dataset-file <file> --essay-number <number> --shingles-len <number> --sign-number <number> --band-number <number> --threshold <float>")
    sys.exit(2)

# The values inserted are set
for opt, arg in opts:
    if opt == '-h':
        print("Usage: script.py --dataset-file <file> --essay-number <number> --shingles-len <number> --sign-number <number> --band-number <number> --threshold <float>")
        sys.exit()
    elif opt == "--dataset-file":
        dataset_file = arg
    elif opt == "--essay-number":
        essay_number = int(arg)
    elif opt == "--shingles-len":
        shingles_len = int(arg)
    elif opt == "--sign-number":
        sign_number = int(arg)
    elif opt == "--band-number":
        band_number = int(arg)
    elif opt == "--threshold":
        threshold = float(arg)

# The inserted/default values are shown to the user
print("Dataset file:", dataset_file)
print("Number of essays:", essay_number)
print("Shingles length:", shingles_len)
print("Number of signature:", sign_number)
print("Number of bands:", band_number)
print("Threshold:", threshold)

# Classes needed in this program are instanciated with the inserted/default values:
dataprocessor = DataProcessor()
shingling = Shingling(shingles_len)
min_hashing = MinHashing(sign_number)
lsh = LSH(band_number, threshold)

# Here date are extracted from the .zip, then processed and normalized. Lastly the characteristic_matrix is created
essays = extract_data(dataset_file, essay_number)
processed_essays = dataprocessor.process_essays(essays)
characteristic_matrix = shingling.create_characteristic_matrix(processed_essays)

# The signature for the data is created
signature = min_hashing.compute_signature_hash(characteristic_matrix)

# Similar documents are found by the Locality-Sensitive Hashing algorithms, then displayed to the user
similar_documents = lsh.find_similar_pairs(signature)
print('similar documents:', similar_documents)