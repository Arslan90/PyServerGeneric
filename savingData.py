import os
import sys
import subprocess
# import traci
# import sumolib
# import traci.constants as tc
import networkx as nx
import matplotlib.pyplot as plt
import random
import buildCologne
import buildVPA
import cPickle as pickle








random.seed(0)

dict_edges = {}

G = nx.MultiDiGraph()

G = buildCologne.build_nodes(G, "nodes.txt")
G, dict_edges = buildCologne.build_edges(G, "edges.txt")

print "Nbr Nodes:", G.number_of_nodes()
print "Nbr Edges:", G.number_of_edges()



# with open("PyServerLog.txt", "a") as outFile:
outFile = open("PyServerLog.txt", "w")
outFile.write("Nbr Nodes:" + str(G.number_of_nodes()))
outFile.write("\nNbr Edges:" + str(G.number_of_edges()))
outFile.close()

radio_range = 300
netBound1 = (0, 0)
netBound2 = (34288.8, 41946.86)
margin = 0

sumo_VPA = []
omnet_VPA = []

sumo_VPA, omnet_VPA = buildVPA.build_VPA(netBound1, netBound2, margin, "TAPAS_VPA.txt")
print "Nbr VPAs:", len(sumo_VPA), "(SUMO)", len(omnet_VPA), "(OMNET)"

with open("PyServerLog.txt", "a") as outFile:
    outFile.write("\nNbr VPAs:" + str(len(sumo_VPA)) + "(SUMO)" + str(len(omnet_VPA)) + "(OMNET)")

mapped_VPA = []
mapped_Type_VPA = []

mapped_VPA, mapped_Type_VPA = buildVPA.mapping_VPA(G, sumo_VPA, radio_range)


allData = [dict_edges, G, sumo_VPA, omnet_VPA, mapped_VPA, mapped_Type_VPA]

# Save a dictionary into a pickle file.
pickle.dump( allData, open( "save.p", "wb" ) )

# Load the dictionary back from the pickle file.
#favorite_color = pickle.load( open( "save.p", "rb" ) )

