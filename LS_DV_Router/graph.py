# To create randomly generated graphs
import random

# For numpy arrays
import numpy

# Simple class for graphs that we'll be using for assignment 3
# We'll be using an adjacency list representation
class Graph:
  def __init__(self):
    self.adj_list = dict()

  # Add a new node to the graph without any edges
  def add_node(self, node_id):
    self.adj_list[node_id] = []

  # Add an edge to a graph; the nodes must already exist
  def add_edge(self, edge_from, edge_to, edge_weight):
    assert(edge_from in self.adj_list)
    assert(edge_to in self.adj_list)
    self.adj_list[edge_from].append((edge_to, edge_weight))

  # Return adjacency matrix (required by scipy to compute shortest paths and in __str__ method)
  def adj_mat(self):
    num_nodes = len(self.adj_list)
    matrix = [[0 for x in range(num_nodes)] for y in range(num_nodes)]
    for i in range(0, num_nodes):
      for edge in self.adj_list[i]:
        j = edge[0]
        weight = edge[1]
        matrix[i][j] = weight
    return numpy.array(matrix)

  # Use this to print out the graph for debugging
  def __str__(self):
    ret = ""
    ret += str(len(self.adj_list)) + "\n"
    graph_adj_mat = self.adj_mat()
    num_nodes = len(self.adj_list)
    for i in range(0, num_nodes):
      for j in range(i + 1, num_nodes):
        if (graph_adj_mat[i][j] != 0):
          ret += str(i) +  " " + str(j) + " " + str(graph_adj_mat[i][j]) + "\n"
    return ret

# Generate a random undirected graph with a given probability of an edge between any 2 nodes
def gen_rand_graph(num_nodes, edge_probability, max_edge_weight):
  # Add nodes
  graph = Graph()
  for i in range(0, num_nodes):
    graph.add_node(i)

  # Add edges at random
  edge_count = 0
  for j in range(0, num_nodes):
    for k in range(j + 1, num_nodes): # Only consider k > j
      if (random.uniform(0.0, 1.0) < edge_probability):
        edge_weight = random.randint(1, max_edge_weight)
        graph.add_edge(j, k, edge_weight)
        graph.add_edge(k, j, edge_weight)
        edge_count = edge_count + 1

  print("Random graph has " + str(num_nodes) + " nodes, " + str(edge_count) + " edges")
  # Uncomment if you want to print out the graph's adjacency list
  #print("Printing random graph below")
  #print(graph)
  return graph

# Create graph based on supplied file
def graph_from_file(graph_file):
  # Open file
  fh = open(graph_file, "r")

  # Read first line that tells us how many nodes are in the file
  first_line = fh.readline()
  first_line.strip("\n")
  num_nodes = int(first_line) # Will throw an error if the first line is not an integer

  # Add nodes
  graph = Graph()
  print ("num_nodes is ", num_nodes)
  for i in range(0, num_nodes):
    graph.add_node(i)

  # Add edges based on the file
  edge_count = 0
  for line in fh.readlines():
    assert(line != "")
    edge_attributes = line.split()
    edge_from = int(edge_attributes[0])
    edge_to   = int(edge_attributes[1])
    if (edge_from == edge_to):
      raise Exception("Can't have loops in graphs; your graph file has an edge from ", edge_from, " to itself")
    edge_weight = float(edge_attributes[2])
    if (edge_weight == 0):
      raise Exception("Can't have an edge with weight 0 from ", edge_from, " to ", edge_to)
    graph.add_edge(edge_from, edge_to, edge_weight)
    graph.add_edge(edge_to, edge_from, edge_weight)
    edge_count += 1

  print("Graph created from file has " + str(num_nodes) + " nodes, " + str(edge_count) + " edges")
  return graph

# Test harness to test graph.py alone
if __name__ == "__main__":
  tmp = gen_rand_graph(20, 0.5, 100)
  adj_mat = tmp.adj_mat()
  print(".graph output\n", tmp)
  print(" adjacency matrix \n", adj_mat)
