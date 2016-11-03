import os
import sys
import subprocess
import traci
import sumolib
import traci.constants as tc
import networkx as nx
import matplotlib.pyplot as plt
import random
import buildCologne
import buildVPA
import time

def retrieveGraphEdge(edgesDict ,edgeID):
    nodesOfEdge = edgesDict[edgeID]
    return G.get_edge_data(nodesOfEdge[0],nodesOfEdge[1])

def nodesOfEdgedRoute(edgesDict, Route):
    nodesAlongRoad = []
    for i, val in enumerate(Route):
        if i == 0:
            nodesAlongRoad.append(edgesDict[val][0])
        nodesAlongRoad.append(edgesDict[val][1])
    return nodesAlongRoad

def edgesOfNodedRoute(Graph, Route, orignalNodedRoute):
    edgeesAlongRoad = []
    for i in range(0, len(Route)-1):
        if Graph.has_edge(Route[i], Route[i+1]):
            if Graph.number_of_edges(Route[i], Route[i+1]) == 1:
                edges = Graph[Route[i]][Route[i+1]]
                edgeesAlongRoad.append(edges[0]["label"])
            elif Graph.number_of_edges(Route[i], Route[i+1]) > 1:
                edges = Graph[Route[i]][Route[i + 1]]
                rightEdge = orignalNodedRoute[len(edgeesAlongRoad)]
                for j, val in edges.iteritems():
                    if val == rightEdge:
                        break
                edgeesAlongRoad.append(edges[j]["label"])
        else:
            raise ValueError("Unable to retrieve edge between nodes:", Route[i], "&", Route[i+1])
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

def randomNodeID(Graph):
    randomNode = ""
    if (len(Graph.nodes())) > 0:
        randomNode = G.nodes()[random.randrange(0, len(G.nodes()))]
    else:
        raise ValueError("Number of nodes in the network is equal to zero (0)")
    print "[MyProg] RandomNode:", randomNode
    return randomNode

def randomTargetVPA(sumo_VPA):
    if (len(sumo_VPA)) > 0:
        randomVPA = random.randrange(0, len(sumo_VPA()))
    else:
        raise ValueError("Number of nodes in the network is equal to zero (0)")
    print "[MyProg] RandomVPDIndex:", randomVPA
    return randomVPA

def nearestNodeToTarget(Graph, targetNode, nodedRoute = []):
    allResults = []
    nearestNode =""
    nearestDist = sys.maxint
    for i,val in enumerate(nodedRoute):
        if nx.has_path(Graph,val,targetNode):
            currentDist = nx.dijkstra_path_length(Graph, val, targetNode)
            allResults.append((val, currentDist))
            if currentDist < nearestDist:
                nearestNode = val
                nearestDist = currentDist
    # print str(allResults)
    return nearestNode, nearestDist

def nearestNodeToVPA(Graph, edgesDict, map_list, map_type, nodedRoute):
    nearestNodes = ("","")
    nearestDist = sys.maxint
    for i,val in enumerate(nodedRoute):
        if (map_type == "None") or (map_type == None):
            break
        else:
            for j, val2 in enumerate(map_list):
                if map_type == "Node":
                    currentDist = dijkstraPathLength(Graph, val, val2[0])
                    if currentDist < nearestDist:
                        nearestNodes = (val,val2[0])
                        nearestDist = currentDist
                elif map_type == "Edge":
                    fromNode = edgesDict[val2[0]][0]
                    toNode = edgesDict[val2[0]][1]
                    currentDist = dijkstraPathLength(Graph, val, fromNode)
                    if currentDist < nearestDist:
                        nearestNodes = (val, fromNode)
                        nearestDist = currentDist
                    currentDist = dijkstraPathLength(Graph, val, toNode)
                    if currentDist < nearestDist:
                        nearestNodes = (val, fromNode)
                        nearestDist = currentDist
    return nearestNodes, nearestDist

def dijkstraPathLength(Graph, node1, node2):
    if nx.has_path(Graph, node1, node2):
        return nx.dijkstra_path_length(Graph, node1, node2)
    else:
        return sys.maxint

def initAll():
    start_time = time.time()
    random.seed(0)

    dict_edges = {}

    G = nx.MultiDiGraph()

    G = buildCologne.build_nodes(G, "nodes.txt")
    G, dict_edges = buildCologne.build_edges(G, "edges.txt")

    print "Nbr Nodes:", G.number_of_nodes()
    print "Nbr Edges:", G.number_of_edges()

    radio_range = 300
    netBound1 = (0, 0)
    netBound2 = (34288.8, 41946.86)
    margin = 0

    sumo_VPA = []
    omnet_VPA = []

    sumo_VPA, omnet_VPA = buildVPA.build_VPA(netBound1, netBound2, margin, "TAPAS_VPA.txt")
    print "Nbr VPAs:", len(sumo_VPA), "(SUMO)", len(omnet_VPA), "(OMNET)"

    mapped_VPA = []
    mapped_Type_VPA = []

    mapped_VPA, mapped_Type_VPA = buildVPA.mapping_VPA(G, sumo_VPA, radio_range)

    NbrMappedToNodes = 0
    NbrMappedToEdges = 0
    NbrNotMapped = 0

    for i, val in enumerate(mapped_Type_VPA):
        if val == "Node":
            NbrMappedToNodes += 1
        if val == "Edge":
            NbrMappedToEdges += 1
        if (val == "None") or (val == None):
            NbrNotMapped += 1

    print "Nbr Mapped To Node:", NbrMappedToNodes, "To Edge:", NbrMappedToEdges, "To None:", NbrNotMapped
    print("--- %s seconds ---" % (time.time() - start_time))


start_time = time.time()
random.seed(0)

dict_edges = {}

G=nx.MultiDiGraph()

G = buildCologne.build_nodes(G, "nodes.txt")
G, dict_edges = buildCologne.build_edges(G, "edges.txt")

print "Nbr Nodes:", G.number_of_nodes()
print "Nbr Edges:", G.number_of_edges()

radio_range = 300
netBound1 = (0,0)
netBound2 = (34288.8,41946.86)
margin = 0

sumo_VPA = []
omnet_VPA = []

sumo_VPA, omnet_VPA = buildVPA.build_VPA(netBound1, netBound2, margin, "TAPAS_VPA.txt")
print "Nbr VPAs:", len(sumo_VPA), "(SUMO)", len(omnet_VPA), "(OMNET)"

mapped_VPA = []
mapped_Type_VPA = []

# print str(retrieveGraphEdge(G, dict_edges, "9953547#0"))
# print str(retrieveGraphEdge(G, dict_edges, "9953547#0")[1])
#
# for i, val in enumerate(G.edges(data=True)):
#     print i, val



# print str(net.getEdge("9953547#0"))

mapped_VPA, mapped_Type_VPA = buildVPA.mapping_VPA(G, sumo_VPA, radio_range)

NbrMappedToNodes = 0
NbrMappedToEdges = 0
NbrNotMapped = 0

for i, val in enumerate(mapped_Type_VPA):
    if val == "Node":
        NbrMappedToNodes +=1
    if val == "Edge":
        NbrMappedToEdges +=1
    if (val == "None") or (val == None):
        NbrNotMapped +=1

print "Nbr Mapped To Node:", NbrMappedToNodes, "To Edge:", NbrMappedToEdges, "To None:", NbrNotMapped

PORT = 9999
sumoBinary = "/usr/local/bin/sumo"
sumoProcess = subprocess.Popen([sumoBinary, "-c", "/media/DATA/DoctoratTlemcen/Git/mixim/mixim/examples/veins/cologne2H/noTraCI.sumo.cfg", "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)


traci.init(PORT)
step = 0
while step < 5:
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
        nodedRoute = nodesOfEdgedRoute(dict_edges, routes)
        print "[MyProg] Noded route:", str(nodedRoute)
        edgedRoute = edgesOfNodedRoute(G, nodedRoute, routes)
        print "[MyProg] Edged route:", str(edgedRoute)
        if (routes <> edgedRoute) or (len(routes) <> len(edgedRoute)):
            raise ValueError("Original and Edged routes are not the same")

        indexRoadID = indexRoadIDInRoute(roadID, routes)
        rmgNodedRoute = []
        rmgEdgedRoute = []
        if indexRoadID != -1:
            rmgEdgedRoute = edgedRoute[indexRoadID:]
            rmgNodedRoute = nodesOfEdgedRoute(dict_edges, rmgEdgedRoute)

            print "[MyProg] Remaining noded route:", str(rmgNodedRoute)
            # print "[MyProg] Remaining edged route:", str(rmgEdgedRoute)

            # targetVPAIndex = randomTargetVPA(sumo_VPA)
            targetVPAIndex = 5
            # if (len(G.nodes())) > 0:
            # randomNode = randomNodeID()
            # print "[MyProg] Selected RandomNode:", randomNode


            nearNodes, nearDist = nearestNodeToVPA(G,dict_edges, mapped_VPA[targetVPAIndex], mapped_Type_VPA[targetVPAIndex], rmgNodedRoute)
            # nearestNodeToTarget(randomNode, rmgNodedRoute)
            print "[MyProg] NearestNode:", nearNodes, "NearestDist:", nearDist

            indexNearNod = indexNodeIDInRoute(nearNodes[0], rmgNodedRoute)
            if indexNearNod > 0:
                nodedRouteToNear = rmgNodedRoute[:indexNearNod]
                print "[MyProg] Remaining noded route to target:", str(nodedRouteToNear)
                tmpRoute = nodedRouteToNear
                tmpRoute.append(nearNodes[0])
                edgedRouteToNear = edgesOfNodedRoute(G, tmpRoute, rmgEdgedRoute)
                print "[MyProg] Remaining edged route to target:", str(edgedRouteToNear)
                estimatedTimeToNear = 0
                for i, val in enumerate(edgedRouteToNear):
                    estimatedTimeToNear += traci.edge.getTraveltime(val.decode().encode('utf-8'))
                print "[MyProg] Estimated time to arrive to nearest point:", str(estimatedTimeToNear)

            # index = next((road for road in traci.vehicle.getRoute(v<ehID) if road == traci.vehicle.getRoadID(vehID)), -1)
            # index = -1
            # for i, val in enumerate(traci.vehicle.getRoute(vehID)):
            #     # print i, val
            #     if val == traci.vehicle.getRoadID(vehID):
            #         index = i
            #         break
            # # print "Index", traci.vehicle.getRoute(vehID).index(traci.vehicle.getRoadID(vehID))
            # print "Index", index,
            # if index == -1:
            #     tokens = traci.vehicle.getRoadID(vehID).split('_')
            #     nodeID = tokens[0].translate(None, ':')
            #     print "Node", nodeID,
            #     # traci.edge.getCO2Emission(traci.vehicle.getRoadID(vehID))
            #     # net.getEdge(traci.vehicle.getRoadID(vehID))
            # elif index >= 0:
            #     routes = traci.vehicle.getRoute(vehID)
            #     print "\n", str(routes)
            #     print "\n", str(nodesOfEdgedRoute(routes))
            #     print "\n", str(edgesOfNodedRoute(nodesOfEdgedRoute(routes)))
            #     if routes <> edgesOfNodedRoute(nodesOfEdgedRoute(routes)):
            #         print "Conversion is false"
            #     # remainingRoute = traci.vehicle.getRoute(vehID)[index:]
            #     # print str(remainingRoute)
            #     # print str(traci.vehicle.getRoute(vehID))
            # print ""


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




print("--- %s seconds ---" % (time.time() - start_time))