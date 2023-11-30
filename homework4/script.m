clear all
clc
%% Calling the algorithm on the first dataset
k = 4
E = csvread('datasets/example1.dat');
algorithm(E, k, 0);

%% Calling the algorithm on the second dataset
k = 2
E = csvread('datasets/example2.dat');
algorithm(E, k, 1);
%%


function [clusters, L] = algorithm(E, k, num_exp)
    figure_offset = 7 * num_exp;

    % Create the adjacency matrix and visualize sparsity
    A = get_adj_matrix(E);
    figure(1 + figure_offset)
    spy(A)

    % Visualize the graph in 2D and 3D
    visualize_graph(A, 'force', 2 + figure_offset);
    visualize_graph(A, 'force3', 3 + figure_offset);
    plot2d = visualize_graph(A, 'force', 4 + figure_offset);
    plot3d = visualize_graph(A, 'force3', 5 + figure_offset);

    % Perform clustering and color nodes based on clusters
    [L, clusters] = perform_clustering(A, k, plot2d, plot3d);

    % Print the spectrum of Laplacian matrices and colour the plots above
    print_spectrum(get_laplacian(A), 'SA', 6 + figure_offset);
    print_spectrum(L, 'SA', 7 + figure_offset);
end


% Visualize the graph using specified layout
function plot_handle = visualize_graph(A, layout_type, figure_num)

    figure(figure_num)
    plot_handle = plot(graph(A), 'Layout', layout_type);
end


% Perform spectral clustering and color nodes based on clusters
function [L, clusters] = perform_clustering(A, k, plot2d, plot3d)

    % Get normalized laplacian from A
    L = get_norm_laplacian(A);

    % Get the top-k eigenvalues from L and then normalize them
    [V, ~] = eigs(L, k);
    Y = V ./ sum(V .* V, 2).^(1/2);

    % Perform K-means clustering on them
    clusters = kmeans(Y, k);

    % Generate k colours
    colours = hsv(k);

    % Colour each node of the network according to the assigned cluster
    for i = 1 : k
        cluster_members = find(clusters == i);
        highlight(plot2d, cluster_members , 'NodeColor', colours(i,:))
        highlight(plot3d, cluster_members , 'NodeColor', colours(i,:))
    end
end


% Print the spectrum of a matrix
function print_spectrum(matrix, mode, figure_num)

    figure(figure_num)
    [F_V, ~] = eigs(matrix, 2, mode);
    plot(sort(F_V(:,2)), '-*')
end


% Creates a sparse adjacency matrix starting fo the given edge list E
function A = get_adj_matrix(E)
    % Take the two column of the files, containing the two vertices of the
    % edges
    col1 = E(:,1);
    col2 = E(:,2);

    % Calculate how big will the matrix be
    max_ids = max(max(col1, col2));

    % Create the sparse adjacent matrix from the Edges list provided
    As = sparse(col1, col2, 1, max_ids, max_ids);
    A  = full(adjacency(graph(As)));
end


% Create the normalized Laplacian Matrix L = (D^(-1/2)*A*D^(-1/2))
function L = get_norm_laplacian(A)
    % Create the diagonal matrix D starting from the adjacency matrix A
    % The elements on the diagonal are the sum of each respective column
    D = diag(sum(A, 2));

    % Calculate the normalized Laplacian Matrix L from A and D
    L = (D^(-1/2)*A*D^(-1/2));
end


% Create the Laplacian Matrix L = (D - A)
function L = get_laplacian(A)
    % Create the diagonal matrix D starting from the adjacency matrix A
    % The elements on the diagonal are the sum of each respective column
    D = diag(sum(A, 2));

    % Calculate the Laplacian Matrix L from A and D
    L = (D - A);
end