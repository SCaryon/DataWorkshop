import pandas as pd
import numpy as np


def read_graph_data(filename):
    temp_data = pd.read_csv(filename, encoding='gbk')
    graph_nodes = temp_data.columns
    graph_nodes = graph_nodes.tolist()
    graph_matrix = np.array(temp_data).tolist()
    del graph_nodes[0]
    if not graph_nodes[-1]:
        del graph_nodes[-1]
    for temp_list in range(len(graph_nodes)):
        del graph_matrix[temp_list][0]
    return graph_nodes, graph_matrix


def check_graph_data(nodes, matrix):
    matrix = np.array(matrix)
    try:
        rows, columns = matrix.shape
        if rows != columns:
            return False
        if len(nodes) != rows:
            return False
    except:
        return False
    else:
        return True
