# Data should be normalized in order to better perform the similarity tasks. So, here:
#  - Text are converted to lowercase-only text
#  - Any accent is removed
#  - Puntation is removed
#  - New lines character are removed
#  - Special character are removed
#  - White spaces are normalized

# Furthermore improvement could be done by:
#  - Removing stopping words (e.g. or, and)
#  - Removing contractions of words (e.g. aren't/are not)
#  - Uniforming numerical value

import string
import unicodedata
import re
import pandas as pd

class DataProcessor:
    # The constructor for this Class. The default create a new object that will perform all the followings 
    def __init__(self, tolowercase=True, remove_punctuation=True, remove_accents=True, remove_newlines = True, remove_specialchar = True, normalize_whitespace=True):
        self.tolowercase = tolowercase
        self.remove_accents = remove_accents
        self.remove_punctuation = remove_punctuation
        self.remove_newlines = remove_newlines
        self.remove_specialchar = remove_specialchar
        self.normalize_whitespace = normalize_whitespace


    def strip_accents(self, essay):
        # Supposing unicode characher to be in the string "essay", it transforms characters with diacritics into their base characters.
        essay_nfkd = unicodedata.normalize('NFKD', essay)

        # Here the text is encoded in ASCII and each not recognized character is removed. Then, it is decoded into a string once again.
        essay_string = essay_nfkd.encode('ASCII', 'ignore').decode('ascii')

        return essay_string

    def process_essay(self, essay):
        if self.tolowercase:
            essay = essay.lower()

        if self.remove_accents:
            essay = self.strip_accents(essay)

        if self.remove_punctuation:
            essay = ''.join(char for char in essay if char not in string.punctuation)

        if self.remove_newlines:
            essay = essay.replace('\n', '')

        if self.remove_specialchar:
            essay = re.sub(r'[^a-zA-Z0-9\s]', '', essay)

        if self.normalize_whitespace:
            essay = ' '.join(essay.split())

        return essay

    # Here the function is overridden for multiple essays    
    def process_essays(self, essays):
        essayList = []

        for essay in essays:
            processed_essay = self.process_essay(essay)
            if processed_essay is not None:
                essayList.append(processed_essay)

        return essayList
