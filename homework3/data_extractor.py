import gzip
from os.path import join


def extract_data(dataset_file):
    # All the SNAP datasets can be found at: https://snap.stanford.edu/data/
    dataset_path = join('datasets', dataset_file)

    # Read the file GZip containing the stanford web-graph datasets
    with gzip.open(dataset_path) as zipped_file:
 
        # Iterate on the file, for each line:
        for line in zipped_file:

            # Get the individual words of the file
            line  = line.decode('utf-8')
            words = line.split()

            # Skip the line if it is a comment
            if words[0] == '#' or words[0] == '%':
                continue
            # If it is not a comment:
            else:
                # Cast the two words into numbers (node numbers)
                src_node, dst_node = int(words[0]), int(words[1])

                # If it is an self-edge, removes it
                if src_node == dst_node:
                    continue

                # If the source number is higher than the destination number, exchange the two nodes
                elif src_node > dst_node:
                    dst_node, src_node = src_node, dst_node

                # Those two variables are saved to be used in a generator
                yield src_node, dst_node


# When this file is directly executed, extract the data and print each edge between each pair of nodes
if __name__ == '__main__':
    dataset_file = 'web-Stanford.txt.gz'
    for src_node, dst_node in extract_data(dataset_file):
        print(f'edge: {src_node} -> {dst_node}')