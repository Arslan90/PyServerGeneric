import os
import sys
import subprocess
import traci
import sumolib
import traci.constants as tc
import networkx as nx
import matplotlib.pyplot as plt
import random


random.seed(0)


# tools = '/media/DATA/DoctoratTlemcen/SIM_Tools_Arslan/sumo-0.13.1/tools'
# sys.path.append(tools)

#net = sumolib.net.readNet('/media/DATA/DoctoratTlemcen/Git/mixim/mixim/examples/veins/cologne2H/cologne_modified.net.xml')
#net = sumolib.net.readNet('/media/DATA/DoctoratTlemcen/Git/mixim/mixim/examples/veins/cologne2H/cologne.net.xml')
#net = sumolib.net.readNet('/media/DATA/DoctoratTlemcen/SIM_Tools_Arslan/sumo-0.13.1/tools/smallGrid.net.xml')
#net = sumolib.net.readNet('/media/WIN7/Users/Arslan/Downloads/Compressed/TAPASCologne-0.24.0/TAPASCologne-0.24.0/cologne2.net.xml')
#net = sumolib.net.readNet('/media/DATA/DoctoratTlemcen/Experimentations/petite2H_Nothing/noTraCI.sumo.cfg')
net = sumolib.net.readNet('/media/DATA/DoctoratTlemcen/Experimentations/petite2H_Nothing/petitprophet.net.xml')

G=nx.DiGraph()
for Node in net.getNodes():
    G.add_node(Node._id, pos=(Node._coord[0],Node._coord[1]))

for Edge in net.getEdges():
    G.add_edge(Edge._from._id, Edge._to._id, label=Edge.getID(), weight=float(Edge.getLength()))

positions = nx.get_node_attributes(G, 'pos')
nx.draw(G, positions, node_size=250, width=1, with_labels=True)
# plt.show()
# plt.autoscale(enable=True, axis='both', tight=True)


PORT = 9999
sumoBinary = "/usr/local/bin/sumo"
sumoProcess = subprocess.Popen([sumoBinary, "-c", "/media/DATA/DoctoratTlemcen/Experimentations/petite2H_Nothing/noTraCI.sumo.cfg", "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)
#sumoProcess = subprocess.Popen([sumoBinary, "-c", "/media/DATA/DoctoratTlemcen/Experimentations/petite2H_Nothing/noTraCI.sumo.cfg", "--remote-port", str(PORT)])
#sumoProcess = subprocess.Popen([sumoBinary, "-c", "/media/WIN7/Users/Arslan/Downloads/Compressed/TAPASCologne-0.24.0/TAPASCologne-0.24.0/cologne.sumo.cfg", "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)
#sumoProcess = subprocess.Popen([sumoBinary, "-c", "/media/DATA/DoctoratTlemcen/Git/mixim/mixim/examples/veins/cologne2H/noTraCI.sumo.cfg", "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)

# # random.seed(0)
# # traci.init(PORT)
# # step = 0
# # while step < 1200:
# #     traci.simulationStep()
# #     print "[MyProg] Simulation time:", step
# #     vehsIDList = traci.vehicle.getIDList()
# #     totalNbrVeh = len(vehsIDList)
# #     # vehsIDList = traci.simulation.getLoadedIDList()
# #     # totalNbrVeh = len(traci.simulation.getLoadedIDList())
# #     if totalNbrVeh > 0:
# #         for vehicle in vehsIDList:
# #             print "[MyProg] VehID:", vehicle, "RoadID:", traci.vehicle.getRoadID(vehicle), "RouteID:", traci.vehicle.getRouteID(vehicle)
# #         # print "[MyProg] Simulation time:", step
# #         # print "[MyProg] TotalNbrVeh: ", totalNbrVeh
# #         # vehID = vehsIDList[random.randrange(0,totalNbrVeh)]
# #         # # vehID = traci.simulation.getLoadedIDList()[random.randrange(0, totalNbrVeh)]
# #         # print "[MyProg] VehID:",vehID
# #         # print "[MyProg] RoadID:", traci.vehicle.getRoadID(vehID), "RouteID:", traci.vehicle.getRouteID(vehID),
# #     step += 1
# # traci.close()

def nodesOfEdgedRoute(Route = []):
    nodesAlongRoad = []
    for i, val in enumerate(Route):
        edge = net.getEdge(val)
        if i == 0:
            nodesAlongRoad.append(edge._from._id)
        nodesAlongRoad.append(edge._to._id)
    return nodesAlongRoad

def edgesOfNodedRoute(Route = []):
    found = False
    edgeesAlongRoad = []
    for i in range(0, len(Route)-1):
        src_node = net.getNode(Route[i])
        sink_node = net.getNode(Route[i+1])
        for src_edges in src_node.getOutgoing():
            for sink_edges in sink_node.getIncoming():
                if src_edges.getID() == sink_edges.getID():
                    edgeesAlongRoad.append(src_edges.getID())
                    found = True
    if not found:
        raise ValueError("Unable to retrieve edge between nodes:", src_node, "&", sink_node)
    return edgeesAlongRoad

def remainingEdgedRoute(currentEdge, Route = []):
    remainingRoute = []
    index = -1
    for i, val in enumerate(Route):
        if val == currentEdge:
            index = i
            break
    if index >= 0:
        remainingRoute = Route[index:]
    return remainingRoute

def remainingNodedRoute(currentNode, Route = []):
    remainingRoute = []
    index = -1
    for i, val in enumerate(Route):
        if val == currentNode:
            index = i
            break
    if index >= 0:
        remainingRoute = Route[index:]
    return remainingRoute

def indexRoadIDInRoute(currentRoadID, Route = []):
    index = -1
    for i, val in enumerate(Route):
        if val == currentRoadID:
            index = i
            break
    return index

def indexNodeIDInRoute(currentNodeID, Route = []):
    index = -1
    for i, val in enumerate(Route):
        if val == currentNodeID:
            index = i
            break
    return index

def extractNodeIDFromInvalidRoadID(currentRoadID):
    nodeID = ""
    tokens = currentRoadID.split('_')
    nodeID = tokens[0].translate(None, ':')
    if nodeID == "":
        raise ValueError("Unable to extract currentNodeID from InvalidRoadID")
    return nodeID

def randomNodeID():
    randomNode = ""
    if (len(G.nodes())) > 0:
        randomNode = G.nodes()[random.randrange(0, len(G.nodes()))]
    else:
        raise ValueError("Number of nodes in the network is equal to zero (0)")
    print "[MyProg] RandomNode:", randomNode
    return randomNode

def nearestNodeToTarget(targetNode, nodedRoute = []):
    allResults = []
    nearestNode =""
    nearestDist = sys.maxint
    for i,val in enumerate(nodedRoute):
        if nx.has_path(G,val,targetNode):
            currentDist = nx.dijkstra_path_length(G, val, targetNode)
            allResults.append((val, currentDist))
            if currentDist < nearestDist:
                nearestNode = val
                nearestDist = currentDist
    # print str(allResults)
    return nearestNode, nearestDist


traci.init(PORT)
step = 0
while step < 100:
    traci.simulationStep()
    vehsIDList = traci.vehicle.getIDList()
    totalNbrVeh = len(vehsIDList)
    if totalNbrVeh > 0:
        print "[MyProg] Simulation time:", step,"TotalNbrVeh:", totalNbrVeh, "\n"
        vehID = vehsIDList[random.randrange(0,totalNbrVeh)]
        roadID = traci.vehicle.getRoadID(vehID)
        routeID = traci.vehicle.getRouteID(vehID)
        routes = traci.vehicle.getRoute(vehID)
        print "[MyProg] VehID:", vehID, "RoadID:", roadID, "RouteID:", routeID
        print "[MyProg] Original route:", str(routes)
        nodedRoute = nodesOfEdgedRoute(routes)
        # print "[MyProg] Noded route:", str(nodedRoute)
        edgedRoute = edgesOfNodedRoute(nodedRoute)
        # print "[MyProg] Edged route:", str(edgedRoute)
        if (routes <> edgedRoute) or (len(routes) <> len(edgedRoute)):
            raise ValueError("Original and Edged routes are not the same")

        indexRoadID = indexRoadIDInRoute(roadID, routes)
        rmgNodedRoute = []
        rmgEdgedRoute = []
        if indexRoadID == -1:
            currentNodeID = extractNodeIDFromInvalidRoadID(roadID)
            rmgNodedRoute = remainingNodedRoute(currentNodeID, nodedRoute)
            rmgEdgedRoute = edgesOfNodedRoute(rmgNodedRoute)
        else:
            rmgEdgedRoute = edgedRoute[indexRoadID:]
            rmgNodedRoute = nodesOfEdgedRoute(rmgEdgedRoute)

        print "[MyProg] Remaining noded route:", str(rmgNodedRoute)
        # print "[MyProg] Remaining edged route:", str(rmgEdgedRoute)

        # if (len(G.nodes())) > 0:
        randomNode = randomNodeID()
        # print "[MyProg] Selected RandomNode:", randomNode

        nearNode, nearDist = nearestNodeToTarget(randomNode, rmgNodedRoute)
        print "[MyProg] NearestNode:", nearNode, "NearestDist:", nearDist

        indexNearNod = indexNodeIDInRoute(nearNode, rmgNodedRoute)
        if indexNearNod > 0:
            nodedRouteToNear = rmgNodedRoute[:indexNearNod]
            print "[MyProg] Remaining noded route to target:", str(nodedRouteToNear)
            tmpRoute = nodedRouteToNear
            tmpRoute.append(nearNode)
            edgedRouteToNear = edgesOfNodedRoute(tmpRoute)
            print "[MyProg] Remaining edged route to target:", str(edgedRouteToNear)
            estimatedTimeToNear = 0
            for i, val in enumerate(edgedRouteToNear):
                estimatedTimeToNear += traci.edge.getTraveltime(val.decode().encode('utf-8'))
            print "[MyProg] Estimated time to arrive to nearest point:", str(estimatedTimeToNear)

        # index = next((road for road in traci.vehicle.getRoute(v<ehID) if road == traci.vehicle.getRoadID(vehID)), -1)
        index = -1
        for i, val in enumerate(traci.vehicle.getRoute(vehID)):
            # print i, val
            if val == traci.vehicle.getRoadID(vehID):
                index = i
                break
        # print "Index", traci.vehicle.getRoute(vehID).index(traci.vehicle.getRoadID(vehID))
        print "Index", index,
        if index == -1:
            # totalInvalidIndex+=1
            tokens = traci.vehicle.getRoadID(vehID).split('_')
            nodeID = tokens[0].translate(None, ':')
            print "Node", nodeID,
            # traci.edge.getCO2Emission(traci.vehicle.getRoadID(vehID))
            # net.getEdge(traci.vehicle.getRoadID(vehID))
        elif index >= 0:
            routes = traci.vehicle.getRoute(vehID)
            print "\n", str(routes)
            print "\n", str(nodesOfEdgedRoute(routes))
            print "\n", str(edgesOfNodedRoute(nodesOfEdgedRoute(routes)))
            if routes <> edgesOfNodedRoute(nodesOfEdgedRoute(routes)):
                print "Conversion is false"
            # remainingRoute = traci.vehicle.getRoute(vehID)[index:]
            # print str(remainingRoute)
            # print str(traci.vehicle.getRoute(vehID))
        print ""


        #print str(traci.vehicle.getRoute(vehID))
        #print "Route edges:", str(traci.vehicle.getRoute(vehID)).strip('[]')
        #print "Remaining route edges:", str(traci.vehicle.getRoute(vehID)).strip('[]')
        # if (len(G.nodes())) > 0:
        #     randomNode = G.nodes()[random.randrange(0,len(G.nodes()))]
            #print "RandomNode: ", randomNode
    print ""
    step += 1

# for i, val in enumerate(traci.edge.getIDList()):
#     print i, val

traci.close()




































#
# # # graph = {'A': ['B', 'C'],
# # #          'B': ['C', 'D'],
# # #          'C': ['D'],
# # #          'D': ['C'],
# # #          'E': ['F'],
# # #          'F': ['C']}
# # #
# # #
# # # def find_path(graph, start, end, path=[]):
# # #     path = path + [start]
# # #     if start == end:
# # #         return path
# # #     if not graph.has_key(start):
# # #         return None
# # #     for node in graph[start]:
# # #         if node not in path:
# # #             newpath = find_path(graph, node, end, path)
# # #             if newpath: return newpath
# # #     return None
# # #
# # # print find_path(graph, 'A', 'D')
# #
# #
# #
# #     #node_dict[Node._id] =
# #
# # #pos = G
# #
# # Edge_labels= []
# # edgeLabel_dict ={}
# #
# # for Edge in net.getEdges():
# #     #print "EdgeID", str(Edge.getID()), "with length", str(Edge.getLength()), " : from ",str(Edge._from._id), " to ", str(Edge._to._id)
# #     G.add_edge(Edge._from._id,Edge._to._id, label=Edge.getID(), weight=Edge.getLength())
# #     Edge_labels.append(Edge.getLength())
# #     edgeLabel_dict[Edge.getID()] = Edge.getLength()
# #
# # #pos=nx.spring_layout(G)
# #
# # nx.draw(G, nx.get_node_attributes(G, 'pos'), with_labels=True)
# # #G.edges(data='weight')
# #
# # src = '5'
# # sink = '7'
# #
# # print(nx.dijkstra_path(G, '5', '7'))
# # print(nx.dijkstra_path_length(G, src, sink))
# #
# # path = nx.dijkstra_path(G, src, sink)
# #
# # for i, val in enumerate(path):
# #     print i, val
# #     if i < (len(path)-1):
# #         print G.get_edge_data(val, path[i+1])["label"]
# #         print G.get_edge_data(val, path[i + 1])["weight"]
# #
# #
# # print sys.maxint
# # print sys.maxsize
# #
# # print type(G)
# #
# # age = input("Votre age ? \n")
# # print "Votre age est :", age
# #
# #
# #
# #     #print G.get_edge_data(val, val+1)
# #     # for j, val2 in enumerate(nx.dijkstra_path(G, src, sink), start=i+1):
# #     #     print j, val2
# #
# # # for val in enumerate(nx.dijkstra_path(G, src, sink)):
# # #     print val
# # #     # print G.node[val]
# #
# # edgeTest = G.get_edge_data(5,6)
# # #print edgeTest
# # #print G.nodes()
# # #print G.edges(data=True)
# # #print G.neighbors("5")
# #
# # # G2=nx.Graph()
# # # e=[('a','b',0.3),('b','c',0.9),('a','c',0.5),('c','d',1.2)]
# # # G2.add_weighted_edges_from(e)
# # # print(nx.dijkstra_path(G2,'a','d'))
# #
# # #nx.draw_networkx_edge_labels(G, nx.get_node_attributes(G, 'pos'))
# # #nx.draw(G, with_labels=True)
# # #plt.show()
# #
