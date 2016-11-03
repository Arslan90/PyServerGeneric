import os
import sys
#if 'SUMO_HOME' in os.environ:
#    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
#    sys.path.append(tools)
#else:
#    sys.exit("please declare environment variable 'SUMO_HOME'")
tools = '/media/DATA/DoctoratTlemcen/SIM_Tools_Arslan/sumo-0.13.1/tools'
sys.path.append(tools)
import sumolib
#net = sumolib.net.readNet()
#print net.getNode('1/1').getCoord()
#print net.getNodes()
#for Node in  net.getNodes():
#    print Node.getID()
#    print Node.getCoord()
#net = sumolib.net.readNet('/media/DATA/DoctoratTlemcen/Git/mixim/mixim/examples/veins/cologne2H/cologne_modified.net.xml')
#net = sumolib.net.readNet('/media/DATA/DoctoratTlemcen/Git/mixim/mixim/examples/veins/cologne2H/cologne.net.xml')
#net = sumolib.net.readNet('/media/DATA/DoctoratTlemcen/SIM_Tools_Arslan/sumo-0.13.1/tools/smallGrid.net.xml')
#net = sumolib.net.readNet('/media/WIN7/Users/Arslan/Downloads/Compressed/TAPASCologne-0.24.0/TAPASCologne-0.24.0/cologne2.net.xml')
#net = sumolib.net.readNet('/media/DATA/DoctoratTlemcen/Experimentations/petite2H_Nothing/noTraCI.sumo.cfg')
net = sumolib.net.readNet('/media/DATA/DoctoratTlemcen/Experimentations/petite2H_Nothing/petitprophet.net.xml')
# print len(net.getNodes())
# for Node in  net.getNodes():
     # print Node._id
     # print Node._coord
     # print "Outgoing edges"
     # for Edge in  Node.getOutgoing():
     #     print Edge.getID()
     # print "Incoming edges"
     # for Edge2 in Node.getIncoming():
     #    print Edge2.getID()
#    print Node.getCoord()




import subprocess
PORT = 9999
sumoBinary = "/usr/local/bin/sumo"
sumoProcess = subprocess.Popen([sumoBinary, "-c", "/media/DATA/DoctoratTlemcen/Experimentations/petite2H_Nothing/noTraCI.sumo.cfg", "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)
#sumoProcess = subprocess.Popen([sumoBinary, "-c", "/media/WIN7/Users/Arslan/Downloads/Compressed/TAPASCologne-0.24.0/TAPASCologne-0.24.0/cologne.sumo.cfg", "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)
#sumoProcess = subprocess.Popen([sumoBinary, "-c", "/media/DATA/DoctoratTlemcen/Git/mixim/mixim/examples/veins/cologne2H/noTraCI.sumo.cfg", "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)

import traci
import traci.constants as tc
traci.init(PORT)
step = 0

#print(traci.simulation.getDistance2D(7684.16, 13583.56, 21483.13, 18133.37, isGeo=False, isDriving=True))
srcNode = net.getNode("5")
sinkNode = net.getNode("7")
while step < 20:
    if step ==1:
        #print(traci.simulation.getDistance2D(110, 100, 210, 100, isGeo=False, isDriving=False))
        #print(traci.simulation.getDistance2D(110, 100, 210, 100, isGeo=False, isDriving=False))
        #print(traci.simulation.getDistanceRoad("B1R", 0, "B1", 0, isDriving=False))
        #print(traci.simulation.getDistanceRoad("B1R", 0, "B1", 0, isDriving=True))
        for OutEdge in srcNode.getIncoming():
            for InEdge in sinkNode.getIncoming():
                #print InEdge.getID()
                #print OutEdge.getID()
                driveDist = traci.simulation.getDistanceRoad(str(OutEdge.getID()), 0, str(InEdge.getID()), InEdge._length, isDriving=True)
                airDist = traci.simulation.getDistanceRoad(str(OutEdge.getID()), 0, str(InEdge.getID()), InEdge._length, isDriving=False)
                #print "For InEdge ", str(InEdge.getID()), "For OutEdge ", str(OutEdge.getID()), "Air Dist ", airDist, "Driving Dist ", driveDist
                #print "Air distance", airDist
                #print "Driving distance", driveDist


        #print(traci.simulation.getNetBoundary())
#        print(sys.float_info.max)
    traci.simulationStep()
#   no = traci.inductionloop.getLastStepVehicleNumber("0")
#   traci.trafficlights.setRedYellowGreenState("0", "GrGr")
    step += 1

#print len(traci.junction.getIDList())
# for string in  traci.junction.getIDList():
#     print string



#print traci.simulation.getDistance2D(110.0, 200.0, 310.0, 0.0, True, False)

#print traci.simulation.getDistance2D(110.0, 200.0, 310.0, 0.0, False, False)

#print traci.simulation.getDistance2D(110.0, 200.0, 310.0, 0.0, True, True)

traci.close()

# graph = {'A': ['B', 'C'],
#          'B': ['C', 'D'],
#          'C': ['D'],
#          'D': ['C'],
#          'E': ['F'],
#          'F': ['C']}
#
#
# def find_path(graph, start, end, path=[]):
#     path = path + [start]
#     if start == end:
#         return path
#     if not graph.has_key(start):
#         return None
#     for node in graph[start]:
#         if node not in path:
#             newpath = find_path(graph, node, end, path)
#             if newpath: return newpath
#     return None
#
# print find_path(graph, 'A', 'D')
import networkx as nx
import matplotlib.pyplot as plt

G=nx.DiGraph()

node_dict = {}

for Node in net.getNodes():
    G.add_node(Node._id, pos=(Node._coord[0],Node._coord[1]))
    #node_dict[Node._id] =

#pos = G

Edge_labels= []
edgeLabel_dict ={}

for Edge in net.getEdges():
    #print "EdgeID", str(Edge.getID()), "with length", str(Edge.getLength()), " : from ",str(Edge._from._id), " to ", str(Edge._to._id)
    G.add_edge(Edge._from._id,Edge._to._id, label=Edge.getID(), weight=Edge.getLength())
    Edge_labels.append(Edge.getLength())
    edgeLabel_dict[Edge.getID()] = Edge.getLength()

#pos=nx.spring_layout(G)

nx.draw(G, nx.get_node_attributes(G, 'pos'), with_labels=True)
#G.edges(data='weight')

src = '5'
sink = '7'

print(nx.dijkstra_path(G, '5', '7'))
print(nx.dijkstra_path_length(G, src, sink))

path = nx.dijkstra_path(G, src, sink)

for i, val in enumerate(path):
    print i, val
    if i < (len(path)-1):
        print G.get_edge_data(val, path[i+1])["label"]
        print G.get_edge_data(val, path[i + 1])["weight"]


print sys.maxint
print sys.maxsize

print type(G)

age = input("Votre age ? \n")
print "Votre age est :", age



    #print G.get_edge_data(val, val+1)
    # for j, val2 in enumerate(nx.dijkstra_path(G, src, sink), start=i+1):
    #     print j, val2

# for val in enumerate(nx.dijkstra_path(G, src, sink)):
#     print val
#     # print G.node[val]

edgeTest = G.get_edge_data(5,6)
#print edgeTest
#print G.nodes()
#print G.edges(data=True)
#print G.neighbors("5")

# G2=nx.Graph()
# e=[('a','b',0.3),('b','c',0.9),('a','c',0.5),('c','d',1.2)]
# G2.add_weighted_edges_from(e)
# print(nx.dijkstra_path(G2,'a','d'))

#nx.draw_networkx_edge_labels(G, nx.get_node_attributes(G, 'pos'))
#nx.draw(G, with_labels=True)
#plt.show()

