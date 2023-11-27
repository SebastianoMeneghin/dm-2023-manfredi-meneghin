import random
import itertools
from collections import defaultdict
from data_extractor import extract_data


class SubGraph:
    """
    Represents the subgraph G containing only the edges of a specific sample S.
    This is implented thanks to adjacency lists and and a set of edges.
    """

    # Initializes the SubGraph instance, with an empty dictionary of adjacency list and an empty set of edges
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.adj_elem = defaultdict(set)
        self.edges = set()


    # Add an edge to the graph
    def add_edge(self, u, v):

        # Add the edge to both the adjacency lists, as if the subgraph were undirected
        self.adj_elem[u].add(v)
        self.adj_elem[v].add(u)

        # Add the edge to the set of edges
        self.edges.add((u, v))

        # If the tag verbose, print the addition of the edge
        if self.verbose:
            print(f'Adding edge ({u}, {v})')
            print(f'N({u}) = {self.adj_elem[u]}, N({v}) = {self.adj_elem[v]}')


    # Remove an edge from the graph
    def remove_edge(self, u, v):
        # Remove the edge from both the adjacency lists, as if the subgraph were undirected
        self.adj_elem[u].remove(v)
        self.adj_elem[v].remove(u)

        # Remove the edge from the set of edges
        self.edges.remove((u, v))

        # If the tag is verbose, print the removal of the edge
        if self.verbose:
            print(f'Removing edge ({u}, {v})')
            print(f'N({u}) = {self.adj_elem[u]}, N({v}) = {self.adj_elem[v]}')

        # If the nodes have now degree zero (they are isolated nodes), remove their entries from the adjacency list
        if not self.adj_elem[u]:
            del self.adj_elem[u]
        if not self.adj_elem[v]:
            del self.adj_elem[v]


    # Return true if the node u is present, false otherwise
    def has_node(self, u):
        return u in self.adj_elem


    # Return true if an edge between u and v is present, false otherwise
    def has_edge(self, u, v):
        return (u, v) in self.edges


    # Get the nodes of the subgraph
    def get_nodes(self):
        return list(self.adj_elem)


    # Get the edges of the subgraph
    def get_edges(self):
        return list(self.edges)
 

    # Get the adjacency list of the node u (all its neighbors)
    def get_neighbors(self, u):
        return self.adj_elem.get(u)



class TriestBase:
    """
    Implementation of the Triest-Base Algorithm
    """

    # Initialize the instance of TriestBase, and its attributes, with default or passed values
    def __init__(self, M, verbose=False):
        self.M = M
        self.verbose = verbose
        self.subgraph = SubGraph(verbose)
        self.global_counter = 0
        self.local_counters = defaultdict(int)

    # Update global and local counters according to the passed operator (+ or -)
    def update_counters(self, operator, u, v):
        # Ensure that both nodes this edge leads to are in the subgraph
        if not self.subgraph.has_node(u) or not self.subgraph.has_node(v):
            return

        # Get neighbors of nodes u and v in the subgraph
        neighbors_u = self.subgraph.get_neighbors(u)
        neighbors_v = self.subgraph.get_neighbors(v)

        # Find the shared neighbors between u and v
        shared_neighbors = neighbors_u & neighbors_v

        # Determine the increment value based on the operator
        incr_value = 0
        if operator == '+':
            incr_value = 1
        else:
            incr_value = -1

        # Update the global/local counters for each shared neighbor
        for neighbour in shared_neighbors:
            # Update global counter
            self.global_counter += incr_value
            # Update local counters for shared neighbor, u, and v
            self.local_counters[neighbour] += incr_value
            self.local_counters[u]         += incr_value
            self.local_counters[v]         += incr_value

        # If the operator is '-', delete local counters containing a value of 0
        if operator == '-':
            # Iterate over shared neighbors, u, and v
            for neighbour in itertools.chain(shared_neighbors, (u, v)):
                # Check if local counter is 0 and delete if true
                if not self.local_counters[neighbour]:
                    del self.local_counters[neighbour]


    # Returns true or false depending whether it is possible to add the node or not to the graph
    def sample_edge(self, t):
        # If t is lower than the value of M, insert insert the edge (base case)
        if t <= self.M:
            return True

        # If not, try to flip a coin, with unequal probability M/t of getting an head
        elif random.random() < (self.M / t):

            # Obtain a random edge from the set of edges
            edge_list = self.subgraph.get_edges()
            w, z = random.choice(edge_list)

            # remove the sampled edge from subgraph
            self.subgraph.remove_edge(w, z)
            self.update_counters('-', w, z)
            return True

        return False


    # Calculate eta given a specific value of t
    def calculate_eta(self, t):
        return max(1, int(t)*(int(t)-1)*(int(t)-2) / (self.M*(self.M-1)*(self.M-2)))


    # This is the main function of the class
    # It implements the algorithm for Triest Base
    def algorithm(self, dataset_file):

        # Extract the edge stream from the dataset file and initialize t
        edge_stream = extract_data(dataset_file)
        t = 0

        # Iterate over each edge in the edge stream
        for u, v in edge_stream:
            # Make sure this edge is not present in our subgraph
            if self.subgraph.has_edge(u, v):
                continue

            t += 1

            # If the edge can be added (t < M or t/M probability of getting head)
            if self.sample_edge(t):
                # Add the edge to the subgraph
                self.subgraph.add_edge(u, v)

                # Update the counters for the added edge
                self.update_counters('+', u, v)

        # Compute the estimate for the global/local triangle counts
        eta_t = self.calculate_eta(t)
        global_triangles = int(eta_t * self.global_counter)

        # Print results
        print(f'M: {self.M}, dataset_name: {dataset_file}')
        print(f'Global triangles estimate: {global_triangles}')

        # If verbose mode is enabled, print local triangles estimate
        if self.verbose:
            # Create a new empty dictionary
            local_triangles = {}

            # Iterate over each node and its counter in local_counters
            for u, counter in self.local_counters.items():
                # Calculate the local triangles estimate for the current node u
                local_triangles[u] = int(eta_t * counter)

            print(f'Local triangles estimate: {local_triangles}')

        return global_triangles
    


class TriestImpr:
    """
    Implementation of the Triest Improved Algorithm
    """

    # Initialize the instance of TriestImproved, and its attributes, with default or passed values
    def __init__(self, M, verbose=False):
        self.M = M
        self.verbose = verbose
        self.subgraph = SubGraph(verbose)
        self.global_counter = 0
        self.local_counters = defaultdict(int)


    # Update global and local counters according to the passed operator (+ or -)
    def update_counters(self, t, u, v):
        # Ensure that both nodes this edge leads to are in the subgraph
        if not self.subgraph.has_node(u) or not self.subgraph.has_node(v):
            return

        # Get neighbors of nodes u and v in the subgraph
        neighbors_u = self.subgraph.get_neighbors(u)
        neighbors_v = self.subgraph.get_neighbors(v)

        # Find the shared neighbors between u and v
        shared_neighbors = neighbors_u & neighbors_v

        # Get the incremental value according to the calculation of eta on t
        incr_value = self.calculate_eta(t)

        # Update the global/local counters for each shared neighbor
        for neighbour in shared_neighbors:
            # Update global counter
            self.global_counter += incr_value
            # Update local counters for shared neighbor, u, and v
            self.local_counters[neighbour] += incr_value
            self.local_counters[u]         += incr_value
            self.local_counters[v]         += incr_value


    # Returns true or false depending whether it is possible to add the node or not to the graph
    def sample_edge(self, t):
        # If t is lower than the value of M, insert insert the edge (base case)
        if t <= self.M:
            return True

        # If not, try to flip a coin, with unequal probability M/t of getting an head
        elif random.random() < (self.M / t):

            # Obtain a random edge from the set of edges
            edge_list = self.subgraph.get_edges()
            w, z = random.choice(edge_list)

            # remove the sampled edge from subgraph
            self.subgraph.remove_edge(w, z)
            self.update_counters(t, w, z)
            return True

        return False
    

    # Calculate eta given a specific value of t
    def calculate_eta(self, t):
        return max(1, (int(t) - 1)*(int(t) - 2) / (self.M*(self.M-1)))


    # This is the main function of the class
    # It implements the algorithm for Triest Improved
    def algorithm(self, dataset_file):

        # Extract the edge stream from the dataset file and initialize t
        edge_stream = extract_data(dataset_file)
        t = 0

        # Iterate over each edge in the edge stream
        for u, v in edge_stream:
            # Make sure this edge is not present in our subgraph
            if self.subgraph.has_edge(u, v):
                continue

            t += 1
            self.update_counters(t, u, v)

            # If the edge can be added (t < M or t/M probability of getting head)
            if self.sample_edge(t):
                # Add the edge to the subgraph
                self.subgraph.add_edge(u, v)

        # Compute the estimate for the global/local triangle counts
        global_triangles = int(self.global_counter)

        # Print results
        print(f'M: {self.M}, dataset_name: {dataset_file}')
        print(f'Global triangles estimate: {global_triangles}')

        # If verbose mode is enabled, print local triangles estimate
        if self.verbose:
            # Create a new empty dictionary
            local_triangles = {}

            # Iterate over each node and its counter in local_counters
            for u, counter in self.local_counters.items():
                local_triangles[u] = int(counter)
            
            print(f'Local triangles estimate: {local_triangles}')

        return global_triangles