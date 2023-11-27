import matplotlib.pyplot as plt
from homework_classes import TriestBase, TriestImpr


# Create an image containing the plotted results of a certain algorithm over a specified dataset
def draw_plot(triest_class, plot_title, dataset_file, m_values, triangle_count):
    triangle_estimates = []

    # Compute the triangles estimates for each of the sampling numbers M passed
    for m in m_values:
        # Instanciate the class, call the algorithm and append the estimate to the list
        triest = triest_class(m)
        triangles = triest.algorithm(dataset_file)
        triangle_estimates.append(triangles)

    # Set the graphs style's attributes
    plt.title(plot_title)
    plt.plot(m_values, triangle_estimates)
    plt.xlabel('M'); plt.ylabel('Triangles')
    plt.axhline(triangle_count, linestyle=':')

    # Save as an image the graph plotted
    dataset_name = dataset_file.split('.')[0]
    plt.savefig(f'images/{plot_title.lower()}-{dataset_name.lower()}.jpg')
    plt.close()


# When this file is directly executed, both the algorithms are called, with a list of 7 different sampling numbers.
if __name__ == '__main__':

    # An entry of the dictionary is added, having as Value: ([Sampling Values], Real Triangles of the network)
    dataset_files = {
        'web-Stanford.txt.gz': ([5000, 7500, 10000, 15000, 20000, 25000, 40000], 11329473)
        # additional entry can be added here, for examples on different datasets,
    }

    # Call draw_plot on both the algorithms, for each entry of the dictionary
    for dataset_file, (m_values, triangle_count) in dataset_files.items():
        draw_plot(TriestBase, 'Triest Base Estimates', dataset_file, m_values, triangle_count)
        draw_plot(TriestImpr, 'Triest Improved Estimates', dataset_file, m_values, triangle_count)