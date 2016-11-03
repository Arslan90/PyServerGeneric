import os
import sys
import networkx as nx
import matplotlib.pyplot as plt

G=nx.DiGraph()

myFile = open("nodes.txt", "r")
f_line = myFile.readline()
while f_line <> "":
    tokens = f_line.split(' ')
    print tokens[1]
    print tokens[3].translate(None, '[,')
    print tokens[4].translate(None, ']')
    G.add_node(tokens[1], pos=(float(tokens[3].translate(None, '[,')), float(tokens[4].translate(None, ']'))))
    f_line = myFile.readline()
myFile.close()

myFile = open("edges.txt", "r")
f_line = myFile.readline()
while f_line <> "":
    tokens = f_line.split(' ')
    print tokens[1]
    print tokens[3]
    print tokens[5]
    print tokens[7]
    G.add_edge(tokens[3], tokens[5], label=tokens[1], weight=float(tokens[7]))
    # G.add_node(tokens[1], pos=(float(tokens[3].translate(None, '[,')), float(tokens[4].translate(None, ']'))))
    f_line = myFile.readline()
myFile.close()

positions = nx.get_node_attributes(G,'pos')
nx.draw(G, positions, node_size=1, width=0.2)
#nx.draw_networkx_edges(G, positions, edgelist=None, width=0.5)
plt.show()
plt.autoscale(enable=True, axis='both', tight=True)