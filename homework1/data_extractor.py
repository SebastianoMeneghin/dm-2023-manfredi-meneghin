import zipfile
from os.path import join
import pandas as pd

# dataset_file correspond to the file to open, while num_essay allows to specify how many samples we want to take
def extract_data(dataset_file, num_essay=None):
    # datasets_source: https://www.kaggle.com/datasets/nbroad/persaude-corpus-2/
    essays = pd.DataFrame()
    dataset_path = join('datasets', dataset_file)

# Read the zip file containing the dataset:
def extract_data(dataset_file, num_essay=None):
    # datasets_source: https://www.kaggle.com/datasets/nbroad/persaude-corpus-2/
    essays = []
    dataset_path = join('datasets', dataset_file)

    # read the zip file containing the dataset:
    with zipfile.ZipFile(dataset_path) as dataset_zipfile:
        # find the name of the file inside the zip file
        filename = dataset_zipfile.namelist()[0]

        with dataset_zipfile.open(filename) as dataset_file:
            # load the file on a dataframe
            csv_dataset = pd.read_csv(dataset_file)

            # select only the "full_text" column from the DataFrame
            essay_column = csv_dataset['full_text']

            # extract only the first num_essay essays from the dataset
            essays = essay_column.head(num_essay).tolist()

    return essays


#Set some specific default values when this script is executed directly (as main)
if __name__ == '__main__':
    dataset_file = 'persuade_2.0_.zip'
    num_essay = 10

    essays = extract_data(dataset_file, num_essay)
    print(essays)