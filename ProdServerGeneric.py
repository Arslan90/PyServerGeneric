import os
import sys
import subprocess
# import traci

import sumolib
import math
import operator
#import traci.constants as tc
from __builtin__ import enumerate

import myconstants as constx
import networkx as nx
import matplotlib.pyplot as plt
import random
import argparse

import buildCologne
import buildVPA
import time
import socket
import select
import cPickle as pickle
import hashlib
from thread import *
import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool
from collections import defaultdict


##################### Small Classes used #####################

class gridSectorsSpecs:

    def __init__(self, sectorsSpecList = None, isSectorMode = False):
        if sectorsSpecList is None:
            self.rowSectorGrid = -1
            self.colSectorGrid = -1
            self.sectorSizeX = -1
            self.sectorSizeY = -1
            self.sectorOffsetX = -1
            self.sectorOffsetY = -1
            self.nbrSectors = -1
        else:
            self.rowSectorGrid = int(sectorsSpecList[0])
            self.colSectorGrid = int(sectorsSpecList[1])
            self.sectorSizeX = sectorsSpecList[2]
            self.sectorSizeY = sectorsSpecList[3]
            self.sectorOffsetX = sectorsSpecList[4]
            self.sectorOffsetY = sectorsSpecList[5]
            self.nbrSectors = int(self.rowSectorGrid * self.colSectorGrid)
        self.sectorMode = isSectorMode

    def getSectorFromCoordinate(self, coord_X, coord_Y, allowUnvalidCoord = False):
        indexCol = int((coord_X - self.sectorOffsetX) // self.sectorSizeX);
        indexRow = int((coord_Y - self.sectorOffsetY) // self.sectorSizeY);
        if not ((0 <= indexCol < self.colSectorGrid) and (0 <= indexRow < self.rowSectorGrid)):
            if allowUnvalidCoord:
                return -1
            else:
                raise ValueError("unvalid coordinates")
        else:
            return self.getSectorFromRowCol(indexRow, indexCol)

    def getSectorFromRowCol(self, indexRow, indexCol):
        if not ((0 <= indexCol < self.colSectorGrid) and (0 <= indexRow < self.rowSectorGrid)):
            raise ValueError("unvalid indexes for rows and columns")
        indexSector = (indexCol * self.rowSectorGrid) + indexRow;
        return indexSector

    def getRowColFromSector(self, indexSector):
        if not (0 <= indexSector < self.nbrSectors):
            raise ValueError("unvalid sector index")
        indexRow = int(indexSector) % self.rowSectorGrid
        indexCol = int(indexSector) // self.rowSectorGrid
        return indexRow, indexCol




##################### Main Functions #####################

def args_parsing():
    parser = argparse.ArgumentParser(description='Full help for using this production script.')
    parser.add_argument('-i', '--input', help='Input file for network road', required=True)
    parser.add_argument('-x', '--specialInput', help='Special Input file for very huge network road (TAPAS Cologne 0.0.3 like)', required=False, default="")
    parser.add_argument('-b', '--netBoundary', help='Network Boundary with 2 points represented like [(x1,y1);(x2,y2)]', required=True)
    parser.add_argument('-r', '--radioRange', help='WIFI radio range of communication in meters', required=True,
                        type=float)
    parser.add_argument('-c', '--omnetFile', help='Omnet++ configuration file (*.ini) used to extract margin and VPA placement', required=True)
    parser.add_argument('-n', '--nClosest', help='Allow to select only the N closest when Mapping VPA',default='3', type=int)
    parser.add_argument('-ip', '--host', help='IP adress of the server host', default='127.0.0.1')
    parser.add_argument('-p', '--port', help='Port adress of the server host', default=19999, type=int)
    parser.add_argument('-bS', '--buffer', help='Buffer size of the server host', default=4096, type=int)
    # parser.add_argument('-o', '--output', help='Output file name', required=True)
    args = parser.parse_args()

    ## show values ##
    print "Input file for network road:", args.input
    print "Special Input file for networke road:", args.specialInput
    print "Boundary of network road:", args.netBoundary
    print "WIFI Radio range of communication:", args.radioRange
    print "Omnet++ configuration file:", args.omnetFile
    print "N closest to VPA:", args.nClosest
    print "Server host IP:", args.host
    print "Server host port:", args.port
    print "Server host buffer size:", args.buffer
    # print ("Output file: %s" % args.output)

    return args

def extractNetBounds(networkBoundaries):
    netBoundaries = str(networkBoundaries)
    netBoundaries = netBoundaries.replace("[", "")
    netBoundaries = netBoundaries.replace("]", "")
    netBoundaries = netBoundaries.replace("(", "")
    netBoundaries = netBoundaries.replace(")", "")
    tokens = netBoundaries.split(";")
    if len(tokens) != 2:
        raise ValueError("unrecognazible network boundaries")
    netBnd1 = tokens[0].split(",")
    if len(netBnd1) != 2:
        raise ValueError("unrecognazible netBound1")
    netBnd2 = tokens[1].split(",")
    if len(netBnd2) != 2:
        raise ValueError("unrecognazible netBound2")
    return (float(netBnd1[0]),float(netBnd1[1])), (float(netBnd2[0]),float(netBnd2[1]))

def extractMargin(omnetConfigFile):
    margin = 0.0
    omnetFileExist = os.path.isfile(omnetConfigFile)
    if not omnetFileExist:
        raise ValueError("omnet++ configuration file not found")
    else:
        nbrOccurence = 0
        omnetFile = open(omnetConfigFile, "r")
        f_line = omnetFile.readline()
        while f_line <> "":
            if f_line.find("margin") != -1:
                f_line = f_line.replace("\n", "")
                tokens = f_line.split("#")
                if tokens[0].find("margin") != -1:
                    nbrOccurence+= 1
                    validEntry = tokens[0].split("=")
                    if len(validEntry) == 2:
                        if validEntry[0].find("margin") != -1:
                            margin = margin + float(validEntry[1])
                        else:
                            raise ValueError("unable to correctly decode margin entry")
                    else:
                        raise ValueError("unable to correctly decode margin entry")
                if nbrOccurence != 1:
                    raise ValueError("invalid occurance of margin in omnet++ configuration file")
            f_line = omnetFile.readline()
        omnetFile.close()
        print "Margin from Omnet++ configuration file:", margin
    return margin

def extractSectorsSpec(omnetConfigFile):
    sectorsSpecNames = ["rowSectorGrid","colSectorGrid","sectorSizeX","sectorSizeY","sectorOffsetX","sectorOffsetY", "NbrSectors"]
    sectorsSpecValues = [-1,-1,-1,-1,-1,-1,-1]
    sectorSpecs = gridSectorsSpecs()
    omnetFileExist = os.path.isfile(omnetConfigFile)
    if not omnetFileExist:
        raise ValueError("omnet++ configuration file not found")
    else:
        omnetFile = open(omnetConfigFile, "r")
        f_line = omnetFile.readline()
        while f_line <> "":
            for i in range(len(sectorsSpecNames)):
                name = sectorsSpecNames[i]
                if f_line.find(name) != -1:
                    f_line = f_line.replace("\n", "")
                    tokens = f_line.split("#")
                    if tokens[0].find(name) != -1:
                        validEntry = tokens[0].split("=")
                        if len(validEntry) == 2:
                            if validEntry[0].find(name) != -1:
                                sectorsSpecValues[i] = float(validEntry[1])
                            else:
                                raise ValueError("unable to correctly decode sectors specs entry")
                        else:
                            raise ValueError("unable to correctly decode sectors specs entry")
            f_line = omnetFile.readline()
        omnetFile.close()
        sectorsSpecValues[6] = sectorsSpecValues[0] * sectorsSpecValues[1]
        if -1 in sectorsSpecValues:
            print "Unable to retrieve all SectorsSpec, assuming that scenario is not sectorMode"
        else:
            sectorSpecs = gridSectorsSpecs(sectorsSpecValues,True)
            print "SectorsSpec from Omnet++ configuration file:", sectorsSpecValues
    return sectorSpecs

def extractVPAs(omnetConfigFile):
    omnet_VPA_List_Size = 0
    omnet_VPA_List = []
    tmp_VPA_List = []
    omnetFileExist = os.path.isfile(omnetConfigFile)
    if not omnetFileExist:
        raise ValueError("omnet++ configuration file not found")
    else:
        nbrOccurence = 0
        omnetFile = open(omnetConfigFile, "r")
        f_line = omnetFile.readline()
        while f_line <> "":
            if f_line.find("numeroNodes") != -1:
                f_line = f_line.replace("\n", "")
                tokens = f_line.split("#")
                if tokens[0].find("numeroNodes") != -1:
                    nbrOccurence+= 1
                    validEntry = tokens[0].split("=")
                    if len(validEntry) == 2:
                        if validEntry[0].find("numeroNodes") != -1:
                            omnet_VPA_List_Size = omnet_VPA_List_Size + int(validEntry[1])
                        else:
                            raise ValueError("unable to correctly decode numeroNodes entry")
                    else:
                        raise ValueError("unable to correctly decode numeroNodes entry")
                if nbrOccurence != 1:
                    raise ValueError("invalid occurance of numeroNodes in omnet++ configuration file")
            f_line = omnetFile.readline()
        print "Nbr of VPA in Omnet++ configuration file:", omnet_VPA_List_Size
        for i in range(0,omnet_VPA_List_Size):
            tmp_VPA_List.append([0.0,0.0])
        omnetFile.seek(0)
        f_line = omnetFile.readline()
        while f_line <> "":
            if f_line.find("VPA") != -1:
                f_line = f_line.replace("\n", "")
                tokens = f_line.split("#")
                if tokens[0].find("Mobility") != -1:
                    validEntry = tokens[0].split("=")
                    if len(validEntry) == 2:
                        if validEntry[0].find("Mobility.x") != -1:
                            wildCardIndex, index = extractVPAIndex(validEntry[0])
                            value = float(validEntry[1])
                            if wildCardIndex:
                                for i in range(0, omnet_VPA_List_Size):
                                    tmp_VPA_List[i][0] = value
                            else:
                                tmp_VPA_List[index][0] = value
                        elif validEntry[0].find("Mobility.y") != -1:
                            wildCardIndex, index = extractVPAIndex(validEntry[0])
                            value = float(validEntry[1])
                            if wildCardIndex:
                                for i in range(0, omnet_VPA_List_Size):
                                    tmp_VPA_List[i][0] = value
                            else:
                                tmp_VPA_List[index][1] = value
                    else:
                        raise ValueError("unable to correctly decode mobility entry for VPAs")
            f_line = omnetFile.readline()
        omnetFile.close()
        for i, val in enumerate(tmp_VPA_List):
            omnet_VPA_List.append((tmp_VPA_List[i][0], tmp_VPA_List[i][1]))
    return omnet_VPA_List

def createSumoVPAs(omnet_VPA_list, netBound1, netBound2, margin):
    sumo_VPA_List = []
    for i, val in enumerate(omnet_VPA_list):
        sumo_x, sumo_y = omnet2sumo(val[0],val[1], netBound1, netBound2, margin)
        sumo_VPA_List.append((sumo_x,sumo_y))
    return sumo_VPA_List

def buildGraph(netFile, specialNetFile, graph, edgeDict, gridSpecs):
    start_time = time.time()
    sectorNodes = defaultdict(list)
    print "Building graph from :", netFile
    graphSerialized = graph_checkSerialized(netFile)
    print "Graph already serialized? :", graphSerialized
    graphExist = os.path.isfile("serializedGraph.p")
    print "Serialized graph exist ?:", graphExist
    if graphExist and graphSerialized:
        print "Proceeding to unserialization of mapping"
        # Load graph and edgeDict from a pickle file.
        unserializedData = pickle.load( open( "serializedGraph.p", "rb" ) )
        print "Nbr Nodes:", unserializedData[0].number_of_nodes()
        print "Nbr Edges:", unserializedData[0].number_of_edges()
        graph = unserializedData[0]
        edgeDict = unserializedData[1]
        sectorNodes = unserializedData[2]
    else:
        if specialNetFile == "":
            print "New building of graph"
            net = sumolib.net.readNet(netFile)
            for Node in net.getNodes():
                sectorId = -1
                if gridSpecs.sectorMode:
                    sectorId = gridSpecs.getSectorFromCoordinate(Node._coord[0], Node._coord[1], True)
                    sectorNodes[sectorId].append(Node._id)
                graph.add_node(Node._id, pos=(Node._coord[0], Node._coord[1]), sector=sectorId)

            for Edge in net.getEdges():
                graph.add_edge(Edge._from._id, Edge._to._id, label=Edge.getID(), weight=float(Edge.getLength()),
                               maxSpeed=float(Edge.getSpeed()))
                edgeDict[Edge.getID()] = (Edge._from._id, Edge._to._id)
        else:
            print "New building of graph with special build"
            spclNetFile = open(specialNetFile, "r")
            f_line = spclNetFile.readline().replace("\n", "")
            nodeSection = False
            edgeSection = False
            while f_line <> "":
                if f_line == "[Nodes Section]":
                    nodeSection = True
                    edgeSection = False
                if f_line == "[Edges Section]":
                    nodeSection = False
                    edgeSection = True
                if nodeSection and f_line != "[Nodes Section]":
                    tokens = f_line.split(' ')
                    sectorId = -1
                    if gridSpecs.sectorMode:
                        sectorId = gridSpecs.getSectorFromCoordinate(float(tokens[3].translate(None, '[,')), float(tokens[4].translate(None, ']')), True)
                        sectorNodes[sectorId].append(tokens[1])
                    graph.add_node(tokens[1],pos=(float(tokens[3].translate(None, '[,')), float(tokens[4].translate(None, ']'))), sector=sectorId)
                if edgeSection and f_line != "[Edges Section]":
                    tokens = f_line.split(' ')
                    graph.add_edge(tokens[3], tokens[5], label=tokens[1], weight=float(tokens[7]), maxSpeed=float(tokens[9]))
                    edgeDict[tokens[1]] = (tokens[3], tokens[5])
                f_line = spclNetFile.readline().replace("\n", "")
            spclNetFile.close()

        # Save graph and edgeDict to a pickle file.
        serializedData = [graph, edgeDict, sectorNodes]
        pickle.dump(serializedData, open("serializedGraph.p", "wb"), protocol=pickle.HIGHEST_PROTOCOL)

        with open("serializedGraph.log", "a") as outFile:
            outFile = open("serializedGraph.log", "w")
            outFile.write("Network File:" + str(netFile))
            netFileSize = str(os.path.getsize(netFile)).replace("L", "")
            outFile.write("\nNetwork File Size in bytes:" + str(netFileSize))
            hashString = hashlib.sha224(str(netFile)+str(netFileSize)).hexdigest()
            outFile.write("\nHash digest:" + str(hashString))
            outFile.close()

        print "Nbr Nodes:", serializedData[0].number_of_nodes()
        print "Nbr Edges:", serializedData[0].number_of_edges()

    end_time = time.time()
    print "Building duration:", str(end_time - start_time)

    return graph, edgeDict, sectorNodes

def buildVPAMapping(netFile, omnetFile, Graph, DictEdges, sumoVPAs, radioRange, nbrCloseNeighbors):
    start_time = time.time()
    print "Building VPA Mapping"
    mappingSerialized = mapping_checkSerialized(netFile, omnetFile, len(sumoVPAs), radioRange)
    print "Mapping already serialized? :", mappingSerialized
    mappingExist = os.path.isfile("serializedMaps.p")
    print "Serialized mapping exist ?:", mappingExist
    if mappingExist and mappingSerialized:
        print "Proceeding to unserialization of graph"
        # Load neighborhoodType and neighborhoodIDs from a pickle file.
        unserializedData = pickle.load(open("serializedMaps.p", "rb"))
        neighborhoodType = unserializedData[0]
        neighborhoodIDs = unserializedData[1]
    else:
        # Build neighborhoodType, neighborhoodIDs.
        neighborhoodIDs, neighborhoodType = checkVPANeighborhood(Graph, sumoVPAs, radioRange)
        # Save neighborhoodType and neighborhoodIDs to a pickle file.
        serializedData = [neighborhoodType, neighborhoodIDs]
        pickle.dump(serializedData, open("serializedMaps.p", "wb"), protocol=pickle.HIGHEST_PROTOCOL)

        with open("serializedMaps.log", "a") as outFile:
            outFile = open("serializedMaps.log", "w")

            outFile.write("Network File:" + str(netFile))
            netFileSize = str(os.path.getsize(netFile)).replace("L", "")
            outFile.write("\nNetwork File Size in bytes:" + str(netFileSize))
            hashString = hashlib.sha224(str(netFile) + str(netFileSize)).hexdigest()
            outFile.write("\nHash digest:" + str(hashString))

            outFile.write("\nOmnet File:" + str(omnetFile))
            nbrVPA = len(sumoVPAs)
            outFile.write("\nNbr VPA:" + str(nbrVPA))
            outFile.write("\nRadio range:" + str(radioRange))
            outFile.close()

    end_time = time.time()
    print "Mapping duration:", str(end_time - start_time)
    return neighborhoodType, neighborhoodIDs

def buildPathsForGraph(graph, edgeDict, map_list, map_type, nodesBySector):
    start_time = time.time()
    print "Building Paths for each sector"
    pathSerialized = path_checkSerialized(graph.number_of_nodes(), graph.number_of_edges(), len(map_list))
    print "Paths already serialized? :", pathSerialized
    pathExist = os.path.isfile("serializedPath.p")
    print "Serialized path exist ?:", pathExist
    if pathExist and pathSerialized:
        print "Proceeding to unserialization of paths"
        # Load graph and edgeDict from a pickle file.
        unserializedData = pickle.load( open( "serializedPath.p", "rb" ) )
        pathDistNodesBySector = unserializedData[0]
    else:
        print "New building of paths between sector nodes and those mapped to VPA"
        pathDistNodesBySector = defaultdict(defaultDictForList)
        for k, v in nodesBySector.iteritems():
            if k == -1:
                continue
            else:
                sub_sub_start_time = time.time()
                listVPAs = []
                if map_type[k] is None or map_type[k] == "None":
                    continue
                for e in map_list[k]:
                    if map_type[k] == "Node":
                        listVPAs.append(e[0])
                    elif map_type[k] == "Edge":
                        listVPAs.append(edgeDict[e[0]][0])
                        listVPAs.append(edgeDict[e[0]][1])
                listVPAs = uniqueInList(listVPAs)
                listNodes = v
                for node1 in listNodes:
                    if node1 in listVPAs:
                        continue
                    for node2 in listVPAs:
                        if node1 == node2 or not nx.has_path(graph, node1, node2) or node2 in pathDistNodesBySector[
                            node1]:
                            continue
                        else:
                            length, path = nx.single_source_dijkstra(graph, node1, node2)
                            # sectorNodesPathDistOtherNodes[node1][node2].append(length[node2])
                            # sectorNodesPathDistOtherNodes[node1][node2].append(path[node2])
                            for l in length:
                                if l in listVPAs and not l in pathDistNodesBySector[node1]:
                                    listLen = length[l]
                                    listPath = path[l]
                                    pathDistNodesBySector[node1][l].append(listLen)
                                    pathDistNodesBySector[node1][l].append(listPath)
                sub_sub_start_time = time.time() - sub_sub_start_time
                print "Building duration for sub nodes path of Sector n", k, ":", sub_sub_start_time

        # Save graph and edgeDict to a pickle file.
        serializedData = [pathDistNodesBySector]
        pickle.dump(serializedData, open("serializedPath.p", "wb"), protocol=pickle.HIGHEST_PROTOCOL)

        with open("serializedPath.log", "a") as outFile:
            outFile = open("serializedPath.log", "w")
            outFile.write("Nbr Nodes:" + str(graph.number_of_nodes()))
            outFile.write("\nNbr Edges:" + str(graph.number_of_edges()))
            outFile.write("\nNbr VPAs:" + str(len(map_list)))
            outFile.close()

    end_time = time.time()
    print "Building paths duration:", str(end_time - start_time)

    return pathDistNodesBySector

def initiateServerSocket(arguments):
    HOST = arguments.host # by default LocalHost 127.0.0.1
    PORT = arguments.port # by default Port 19999
    if not (0 <= PORT <= (2**16-1)):
        raise ValueError("Unvalid port number")
    RECV_BUFFER = arguments.buffer # by default 4096

    Server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Server_socket.bind((HOST, PORT))
    Server_socket.listen(0)

    return HOST, PORT, RECV_BUFFER, Server_socket


# Function for handling connections. This will be used to create threads
def clientthread(conn, addr, buffer, serv_vars):
    # infinite loop so that function do not terminate and thread do not end.
    nbrRequest = 0
    while True:

        # Receiving from client
        # time.sleep(0.01)
        data = conn.recv(buffer)
        if data == "CLOSE":
            print "Client (%s, %s) is going offline" % addr
            print "Total requests served to client: ", nbrRequest
            conn.close()
            break
        else:
            nbrRequest +=1
            tmp_str = data
            tokens = tmp_str.split('?')
            for i, val in enumerate(tokens):
                if val == "":
                    continue
                tokens_msg = val.split(';')
                # for j, val2 in enumerate(tokens_msg):
                tokens_command = tokens_msg[0].split(':')
                msg_type = int(tokens_command[0])
                cmd = int(tokens_command[1])
                tokens_args = []
                for j, val2 in enumerate(tokens_msg[1:]):
                    tmp = val2.split(':')
                    tokens_args.append(int(tmp[0]))
                    tokens_args.append(tmp[1])
                if msg_type == constx.QUERY:
                    if cmd in constx.KNOWN_QUERIES:
                        cmd_format = constx.FORMAT_QUERIES[cmd]
                        error = False
                        if len(tokens_args) != len(cmd_format):
                            error = True
                            for j in xrange(2, len(tokens_args), 2):
                                if tokens_msg[j] != cmd_format[j]:
                                    error = True
                        if error:
                            raise ValueError("Error query format")
                        if cmd == constx.CMD_NP_ALL:
                            response_msg = compute_NP_ALL(tokens_args[1], tokens_args[3], serv_vars)
                            conn.send(response_msg)
                        elif cmd == constx.CMD_EDGE_BEST_TRAVEL_TIME:
                            response_msg = compute_EDGE_BEST_TRAVEL_TIME(tokens_args[1], serv_vars)
                            conn.send(response_msg)
                elif msg_type == constx.RESPONSE:
                    print "Not supported for now"
                else:
                    raise ValueError("unrecognazible msg type received")
    #
    # # came out of loop
    # conn.close()

##################### Utility Functions #####################

def defaultDictForList():
    return defaultdict(list)

def uniqueInList(my_list):
    tmp_set = set()
    tmp_list = []
    for obj in my_list:
        if obj not in tmp_set:
            tmp_list.append(obj)
            tmp_set.add(obj)
    return tmp_list

def extractVPAIndex(validStrContainingIndex):
    index = -1
    wildcardIndex = False
    strIndex = validStrContainingIndex[validStrContainingIndex.find("VPA[") + 4:validStrContainingIndex.find("]")]
    if strIndex.isdigit():
        index = int(strIndex)
    elif strIndex == "*":
        wildcardIndex = True
    else:
        raise ValueError("unable to correctly retrieve VPA index")
    return wildcardIndex, index

def graph_checkSerialized(netFile):
    netFileSize = str(os.path.getsize(netFile)).replace("L", "")
    hashString = hashlib.sha224(str(netFile) + str(netFileSize)).hexdigest()

    oldNetFile = ""
    oldNetFileSize = ""
    oldHashString = ""

    serializedLogFileExist = os.path.isfile("serializedGraph.log")
    if serializedLogFileExist:
        serializedLogFile = open("serializedGraph.log", "r")
        f_line = serializedLogFile.readline()
        while f_line <> "":
            tokens = f_line.split(':')
            if tokens[0] == str("Network File"):
                oldNetFile = tokens[1].replace("\n", "")
            if tokens[0] == str("Network File Size in bytes"):
                oldNetFileSize = tokens[1].replace("\n", "")
            if tokens[0] == str("Hash digest"):
                oldHashString = tokens[1].replace("\n", "")
            f_line = serializedLogFile.readline()
        serializedLogFile.close()

    return (serializedLogFileExist) and (netFile == oldNetFile) and (netFileSize == oldNetFileSize) and (hashString == oldHashString)

def mapping_checkSerialized(netFile, omnetFile, nbrVPA, radioRange):
    netFileSize = str(os.path.getsize(netFile)).replace("L", "")
    hashString = hashlib.sha224(str(netFile) + str(netFileSize)).hexdigest()

    oldNetFile = ""
    oldNetFileSize = ""
    oldHashString = ""

    oldOmnetFile = ""

    oldNbrVPA = 0

    oldRadioRange = 0.0

    serializedLogFileExist = os.path.isfile("serializedMaps.log")
    if serializedLogFileExist:
        serializedLogFile = open("serializedMaps.log", "r")
        f_line = serializedLogFile.readline()
        while f_line <> "":
            tokens = f_line.split(':')
            if tokens[0] == str("Network File"):
                oldNetFile = tokens[1].replace("\n", "")
            if tokens[0] == str("Network File Size in bytes"):
                oldNetFileSize = tokens[1].replace("\n", "")
            if tokens[0] == str("Hash digest"):
                oldHashString = tokens[1].replace("\n", "")
            if tokens[0] == str("Omnet File"):
                oldOmnetFile = tokens[1].replace("\n", "")
            if tokens[0] == str("Nbr VPA"):
                oldNbrVPA = int(tokens[1].replace("\n", ""))
            if tokens[0] == str("Radio range"):
                oldRadioRange = float(tokens[1].replace("\n", ""))
            f_line = serializedLogFile.readline()
        serializedLogFile.close()

    return serializedLogFileExist and (netFile == oldNetFile) and (netFileSize == oldNetFileSize) and (hashString == oldHashString) and (omnetFile == oldOmnetFile) and  (nbrVPA == oldNbrVPA) and (radioRange == oldRadioRange)

def path_checkSerialized(nbrNodes, nbrEdges, nbrVPAs):
    oldNbrNodes = 0
    oldNbrEdges = 0
    oldNbrVPAs = 0

    serializedLogFileExist = os.path.isfile("serializedPath.log")
    if serializedLogFileExist:
        serializedLogFile = open("serializedPath.log", "r")
        f_line = serializedLogFile.readline()
        while f_line <> "":
            tokens = f_line.split(':')
            if tokens[0] == str("Nbr Nodes"):
                oldNbrNodes = int(tokens[1].replace("\n", ""))
            if tokens[0] == str("Nbr Edges"):
                oldNbrEdges = int(tokens[1].replace("\n", ""))
            if tokens[0] == str("Nbr VPAs"):
                oldNbrVPAs = int(tokens[1].replace("\n", ""))
            f_line = serializedLogFile.readline()
        serializedLogFile.close()

    return (nbrNodes == oldNbrNodes) and (nbrEdges == oldNbrEdges) and (nbrVPAs == oldNbrVPAs)

def sumo2omnet(sumo_x,sumo_y, netBound1, netBound2, margin):
    omnet_x = sumo_x - netBound1[0] + margin
    omnet_y = (netBound2[1] - netBound1[1]) - (sumo_y - netBound1[1]) + margin
    return omnet_x, omnet_y

def omnet2sumo(omnet_x,omnet_y, netBound1, netBound2, margin):
    sumo_x = omnet_x + netBound1[0] - margin
    sumo_y = (netBound2[1] - netBound1[1]) - (omnet_y - netBound1[1]) + margin
    return sumo_x, sumo_y

def node_inRange_VPA(node_pos, vpa_pos, r):
    sqr_dist = -1
    sqr_dist = (node_pos[0] - vpa_pos[0])**2 + (node_pos[1] - vpa_pos[1])**2
    if sqr_dist <= r**2:
        return True, math.sqrt(sqr_dist)
    else:
        return False, math.sqrt(sqr_dist)

def euclidean_distance(posNode1, posNode2):
    sqr_dist = -1
    sqr_dist = (posNode1[0] - posNode2[0])**2 + (posNode1[1] - posNode2[1])**2
    return math.sqrt(sqr_dist)

def edge_inRange_VPA(node_pos1, node_pos2, vpa_pos, r):
    def dot(v, w):
        # x,y,z = v
        # X,Y,Z = w
        # return x*X + y*Y + z*Z
        return v[0] * w[0] + v[1] * w[1]

    def length(v):
        # x,y,z = v
        # return math.sqrt(x*x + y*y + z*z)
        return math.sqrt(float(v[0]) ** 2 + float(v[1]) ** 2)

    def vector(b, e):
        # x,y,z = b
        # X,Y,Z = e
        # return (X-x, Y-y, Z-z)
        return (e[0] - b[0], e[1] - b[1])

    def unit(v):
        # x,y,z = v
        # mag = length(v)
        # return (x/mag, y/mag, z/mag)
        mag = length(v)
        return (v[0] / mag, v[1] / mag)

    def distance(p0, p1):
        return length(vector(p0, p1))

    def scale(v, sc):
        # x,y,z = v
        # return (x * sc, y * sc, z * sc)
        return (v[0] * sc, v[1] * sc)

    def add(v, w):
        # x,y,z = v
        # X,Y,Z = w
        # return (x+X, y+Y, z+Z)
        return (v[0] + w[0], v[1] + w[1])

    def pnt2line(pnt, start, end):
        line_vec = vector(start, end)
        pnt_vec = vector(start, pnt)
        line_len = length(line_vec)
        line_unitvec = unit(line_vec)
        pnt_vec_scaled = scale(pnt_vec, 1.0 / line_len)
        t = dot(line_unitvec, pnt_vec_scaled)
        if t < 0.0:
            t = 0.0
        elif t > 1.0:
            t = 1.0
        nearest = scale(line_vec, t)
        dist = distance(nearest, pnt_vec)
        nearest = add(nearest, start)
        return nearest, dist

    near_dist = -1
    start = (node_pos1[0], node_pos1[1])
    end = (node_pos2[0], node_pos2[1])
    pnt = (vpa_pos[0], vpa_pos[1])
    near_coord, near_dist = pnt2line(pnt,start,end)
    if near_dist <= r:
        return True, near_dist
    else:
        return False, near_dist

def checkVPANeighborhood(Graph,sumoVPAs,radioRange):
    # This function tries to determine IDs of sumoVPA neighborhood,
    # first it checks for the existance of nodes, then edges and finally
    # marks its as none if nothing
    neighborhoodIDs = []
    neighborhoodType = []
    ############ Try to map VPA to Nodes ##############
    for i, val in enumerate(sumoVPAs):
        map = []
        for j, val2 in enumerate(Graph.nodes(data=True)):
            result = False
            dist = -1
            node_pos = val2[1]["pos"]
            vpa_pos = (val[0], val[1])
            result, dist = node_inRange_VPA(node_pos, vpa_pos, radioRange)
            if result == True:
                map.append((val2[0].decode().encode('utf-8'), dist))
        if map == []:
            neighborhoodType.append(None)
        else:
            neighborhoodType.append("Node")
        neighborhoodIDs.append(map)
    ############ Try to map remaining VPA to Edges ##############
    for i, val in enumerate(sumoVPAs):
        if neighborhoodIDs[i] != []:
            continue
        map = []
        for j, val2 in enumerate(Graph.edges(data=True)):
            result = False
            dist = -1
            node_pos1 = Graph.node[val2[0]]["pos"]
            node_pos2 = Graph.node[val2[1]]["pos"]
            vpa_pos = (val[0], val[1])
            result, dist = edge_inRange_VPA(node_pos1, node_pos2, vpa_pos, radioRange)
            if result == True:
                map.append((val2[2]["label"].decode().encode('utf-8'), dist))
        if map != []:
            neighborhoodType[i] = "Edge"
        neighborhoodIDs[i] = map
        # mapping_list.append(map)
    return neighborhoodIDs, neighborhoodType

def selectVPACloseNeighbors(Graph, Dict_edges, neighborhoodIDs, neighborhoodType, nextNodeInRoute, nbrCloseNeighbors):
    closeNeighborhoodIDs = []
    distances = []
    tmp = []
    posNextNodeInRoute = Graph.node[nextNodeInRoute]["pos"]
    for i, val in enumerate (neighborhoodIDs):
        if neighborhoodType == "Node":
            posNeighborhoodID = Graph.node[val[0]]["pos"]
            tmp.append((val[0], val[1], euclidean_distance(posNextNodeInRoute,posNeighborhoodID)))
        elif neighborhoodType == "Edge":
            NeighborhoodID1 = Dict_edges[val[0]][0]
            NeighborhoodID2 = Dict_edges[val[0]][1]
            posNeighborhoodID1 = Graph.node[NeighborhoodID1]["pos"]
            tmp.append((NeighborhoodID1, val[1], euclidean_distance(posNextNodeInRoute, posNeighborhoodID1)))
            posNeighborhoodID2 = Graph.node[NeighborhoodID2]["pos"]
            tmp.append((NeighborhoodID2, val[1], euclidean_distance(posNextNodeInRoute, posNeighborhoodID2)))
    if neighborhoodType == "Edge":
        tmp_set = set()
        tmp_list = []
        for obj in tmp:
            if obj[0] not in tmp_set:
                tmp_list.append(obj)
                tmp_set.add(obj[0])
        tmp = tmp_list
    if len(neighborhoodIDs) <= nbrCloseNeighbors:
        tmp = sorted(tmp, key=operator.itemgetter(2))
    else:
        tmp = sorted(tmp, key=operator.itemgetter(2))[:nbrCloseNeighbors]
    for k, (id, d, euclid_d) in enumerate(tmp):
        closeNeighborhoodIDs.append((id, d))
        distances.append((id, euclid_d))
    return closeNeighborhoodIDs, distances


def compute_NP_ALL(VPA_ID, Route,  Server_vars):
    Graph, Dict_edges = Server_vars[0], Server_vars[1]
    VPA_Mapping, VPA_Mapping_Type, NbrClosestNbhr = Server_vars[3], Server_vars[2], Server_vars[4]
    pathDistNodesBySector = Server_vars[5]
    service_time = time.time()
    if VPA_Mapping_Type[int(VPA_ID)] is None or VPA_Mapping_Type[int(VPA_ID)] == "None":
        print "Sector ", str(VPA_ID), " mapped to None"
        nearestNodes = ("ND","ND")
        edgesOfNP = ("ND","ND")
        dist = sys.maxint
        edgedRoute_NP_VPA = ["ND"]
    else:
        tokensForEdgedRoute = Route.split(' ')
        edgedRoute = []
        for j, val2 in enumerate(tokensForEdgedRoute):
            edgedRoute.append(val2)
        nodedRoute = nodesOfEdgedRoute(Dict_edges, edgedRoute, WithFirstNode=False)
        nearestNodes, dist, path = nearestNodeToVPA_dist_path(Graph, Dict_edges, VPA_Mapping[int(VPA_ID)],
                                                              VPA_Mapping_Type[int(VPA_ID)], nodedRoute, NbrClosestNbhr, int(VPA_ID), pathDistNodesBySector)
        edgesOfNP = edgesOfNearestPoint(edgedRoute, nearestNodes[1], Dict_edges)
        if edgesOfNP[0] != "ND" and edgesOfNP[1] == "ND":
            print "Must find the edge outgoing from NP in direction of VPA"
            tmp = edgesOfNP[0]
            edgesOfNP = (tmp,"ND") # ND => Not Defined (default value if none)
        if path == "ND":
            edgedRoute_NP_VPA = ["ND"]
        else:
            edgedRoute_NP_VPA, dist_NP_VPA = edgesOfNodedRoute(Graph, path, shortest=True)
    service_time = time.time() - service_time
    print "[VPA_NODE,NP_NODE]", str(nearestNodes), "[Edge->NP, NP->Edge]", edgesOfNP, "[Dist_NP_VPA]", str(
        dist), "[Route_NP_VPA]", str(edgedRoute_NP_VPA), "Service duration", service_time, "\n"
    route_as_string = ""
    for i, val in enumerate(edgedRoute_NP_VPA):
        if i == 0:
            route_as_string = val.decode().encode('utf-8')
        else:
            route_as_string = route_as_string + " " + val.decode().encode('utf-8')
    if edgedRoute_NP_VPA == []:
        route_as_string = " "
    msg = [str(constx.RESPONSE), str(constx.RESPONSE_NP_ALL), str(constx.EDGE_TO_NP), str(edgesOfNP[0]),
           str(constx.NODE_NP), str(nearestNodes[1]), str(constx.EDGE_FROM_NP), str(edgesOfNP[1]),
           str(constx.NODE_VPA_MAPPING), str(nearestNodes[0]), str(constx.ROUTE_NP_VPA), str(route_as_string),
           str(constx.ROUTE_LENGTH_NP_VPA), str(float(dist))]
    msg_as_string = ""
    for j in xrange(0, len(msg), 2):
        msg_as_string = msg_as_string + msg[j].decode().encode('utf-8') + ":" + msg[j + 1].decode().encode('utf-8')
        if j == len(msg) - 2:
            msg_as_string = msg_as_string + "?"
        else:
            msg_as_string = msg_as_string + ";"
    return msg_as_string


def compute_EDGE_BEST_TRAVEL_TIME(EDGE_ID, Server_vars):
    Graph, Dict_edges = Server_vars[0], Server_vars[1]
    travelTime = sys.maxint
    service_time = time.time()
    nodesOfEdge = ("", "")
    nodesOfEdge = Dict_edges[EDGE_ID]
    if (nodesOfEdge != ("", "")) and (Graph.has_edge(nodesOfEdge[0], nodesOfEdge[1])):
        edges = Graph[nodesOfEdge[0]][nodesOfEdge[1]]
        for j, val in edges.iteritems():
            if val["label"] == EDGE_ID:
                if val["maxSpeed"] != 0.0:
                    travelTime = val["weight"] / val["maxSpeed"]
                else:
                    raise ValueError("Edge Max Speed value equals 0.0")
    else:
        raise ValueError("Edge not found")
    service_time = time.time() - service_time
    print "[EDGE_ID]", str(EDGE_ID), "[EDGE_BEST_TRAVEL_TIME]", str(travelTime), "\n"
    msg = [str(constx.RESPONSE), str(constx.RESPONSE_EDGE_BEST_TRAVEL_TIME), str(constx.EDGE_BEST_TRAVEL_TIME),
           str(float(travelTime))]
    msg_as_string = ""
    for j in xrange(0, len(msg), 2):
        msg_as_string = msg_as_string + msg[j].decode().encode('utf-8') + ":" + msg[j + 1].decode().encode('utf-8')
        if j == len(msg) - 2:
            msg_as_string = msg_as_string + "?"
        else:
            msg_as_string = msg_as_string + ";"
    return msg_as_string

def nodesOfEdgedRoute(edgesDict, Route, WithFirstNode = True):
    nodesAlongRoad = []
    for i, val in enumerate(Route):
        if i == 0 and WithFirstNode:
            nodesAlongRoad.append(edgesDict[val][0].decode().encode('utf-8'))
        nodesAlongRoad.append(edgesDict[val][1].decode().encode('utf-8'))
    return nodesAlongRoad

def edgesOfNodedRoute(Graph, Route, orignalNodedRoute):
    edgeesAlongRoad = []
    for i in range(0, len(Route)-1):
        if Graph.has_edge(Route[i], Route[i+1]):
            if Graph.number_of_edges(Route[i], Route[i+1]) == 1:
                edges = Graph[Route[i]][Route[i+1]]
                edgeesAlongRoad.append(edges[0]["label"].decode().encode('utf-8'))
            elif Graph.number_of_edges(Route[i], Route[i+1]) > 1:
                edges = Graph[Route[i]][Route[i + 1]]
                rightEdge = orignalNodedRoute[len(edgeesAlongRoad)]
                for j, val in edges.iteritems():
                    if val == rightEdge:
                        break
                edgeesAlongRoad.append(edges[j]["label"].decode().encode('utf-8'))
        else:
            raise ValueError("Unable to retrieve edge between nodes:", Route[i], "&", Route[i+1])
    return edgeesAlongRoad

def edgesOfNodedRoute(Graph, Route, shortest=True):
    edgeesAlongRoad = []
    totalLength = 0
    for i in range(0, len(Route)-1):
        if Graph.has_edge(Route[i], Route[i+1]):
            edge = ""
            edges = Graph[Route[i]][Route[i + 1]]
            if Graph.number_of_edges(Route[i], Route[i+1]) > 1 and shortest == True:
                for j, val in edges.iteritems():
                    length = sys.maxint
                    if val["weight"] < length:
                        length = val["weight"]
                        edge = val
            else:
                edge = edges[0]
            edgeesAlongRoad.append(edge["label"].decode().encode('utf-8'))
            totalLength += float(edge["weight"])
        else:
            raise ValueError("Unable to retrieve edge between nodes:", Route[i], "&", Route[i+1])
    return edgeesAlongRoad, totalLength

def edgesOfNearestPoint(Route, NP_Node, edgeDict):
    edge_to_NP = "ND"
    edge_from_NP = "ND"
    for j, val2 in enumerate(Route):
        if edge_to_NP != "ND" and edge_from_NP != "ND":
            break
        if edgeDict[val2][0] == NP_Node:
            edge_from_NP = val2.decode().encode('utf-8')
        if edgeDict[val2][1] == NP_Node:
            edge_to_NP = val2.decode().encode('utf-8')
    edgesOfNP = (edge_to_NP, edge_from_NP)
    return edgesOfNP

def nearestNodeToVPA_dist_path(Graph, edgesDict, map_list, map_type, nodedRoute, nbrCloseNeighbors, sectorId, pathDistNodesBySector):
    nearestNodes = ("ND","ND")
    nearestDist = sys.maxint
    nearestPath = "ND"
    closeNeighborhoodIDs, distances = selectVPACloseNeighbors(Graph, edgesDict, map_list, map_type, nodedRoute[0], nbrCloseNeighbors)
    for i, ndMapVPA in enumerate(closeNeighborhoodIDs):
        if (map_type == "None") or (map_type == None):
            break
        elif map_type == "Node" or map_type == "Edge":
            for j, ndNodedRt in enumerate(nodedRoute):
                nodeSectorId = Graph.node[ndNodedRt]["sector"]
                if j == 0 or sectorId == nodeSectorId:
                    bool = nx.has_path(Graph,ndNodedRt, ndMapVPA[0])
                    if bool:
                        if ndMapVPA[0] in pathDistNodesBySector[ndNodedRt]:
                            currentLength = pathDistNodesBySector[ndNodedRt][ndMapVPA[0]][0]
                            currentPath = pathDistNodesBySector[ndNodedRt][ndMapVPA[0]][1]
                        else:
                            length,path = nx.single_source_dijkstra(Graph,ndNodedRt, ndMapVPA[0])
                            currentLength = length[ndMapVPA[0]]
                            currentPath = path[ndMapVPA[0]]
                        if currentLength < nearestDist:
                            nearestNodes = (ndMapVPA[0], ndNodedRt.decode().encode('utf-8'))
                            nearestDist = currentLength
                            nearestPath = currentPath
    return nearestNodes, nearestDist, nearestPath


##################### Function Main() #####################

def main(argv):

    start_time = time.time()
    random.seed(0)

    dict_edges = {}
    G = nx.MultiDiGraph()

    args = args_parsing()
    roadNetwork = args.input
    spclRoadNetFile = args.specialInput
    netBound1, netBound2 = extractNetBounds(args.netBoundary)
    radioRange = args.radioRange
    margin = extractMargin(args.omnetFile)
    omnet_VPAs = extractVPAs(args.omnetFile)
    sumo_VPAs = createSumoVPAs(omnet_VPAs, netBound1, netBound2, margin)

    myGridSectorsSpecs = extractSectorsSpec(args.omnetFile)
    if myGridSectorsSpecs.sectorMode and (myGridSectorsSpecs.nbrSectors != len(omnet_VPAs)):
        raise ValueError("Nbr Sectors don't correspond to Nbr VPAs")


    G, dict_edges, sectorNodes = buildGraph(roadNetwork, spclRoadNetFile, G, dict_edges, myGridSectorsSpecs)

    nbrCloseNeighbors = args.nClosest

    neighborhoodType, neighborhoodIDs = buildVPAMapping(roadNetwork, args.omnetFile, G, dict_edges, sumo_VPAs, radioRange, nbrCloseNeighbors)

    sectorNodesPathDistOtherNodes = buildPathsForGraph(G, dict_edges, neighborhoodIDs, neighborhoodType, sectorNodes)

    NbrMappedToNodes = 0
    NbrMappedToEdges = 0
    NbrNotMapped = 0

    for i, val in enumerate(neighborhoodType):
        if val == "Node":
            NbrMappedToNodes += 1
        if val == "Edge":
            NbrMappedToEdges += 1
        if (val == "None") or (val == None):
            NbrNotMapped += 1

    print ("Nbr Mapped To Node: " + str(NbrMappedToNodes) + " To Edge: " + str(NbrMappedToEdges) + " To None: " + str(
        NbrNotMapped))

    server_vars = (G, dict_edges, neighborhoodType, neighborhoodIDs, nbrCloseNeighbors, sectorNodesPathDistOtherNodes)

    Host, Port, Buffer, server_socket = initiateServerSocket(args)

    # now keep talking with the client
    while True:
        # wait to accept a connection - blocking call
        conn, addr = server_socket.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])

        # start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        start_new_thread(clientthread, (conn, addr, Buffer, server_vars))

    server_socket.close()



















    # mapped_VPA_length_dist = {}
    #
    # for i, val in enumerate(closeNeighborhoodIDs):
    #     # if mapped_Type_VPA[i] != "Node":
    #     if (neighborhoodType[i] == "None") or (neighborhoodType[i] == None):
    #         continue
    #     for j, val2 in enumerate(val):
    #         if neighborhoodType[i] == "Node":
    #             length, path = nx.single_source_dijkstra(G, val2[0])
    #             # mapped_VPA_length_dist[val2[0]] = (length, path)
    #         elif neighborhoodType[i] == "Edge":
    #             fromNode = dict_edges[val2[0]][0]
    #             length, path = nx.single_source_dijkstra(G, fromNode)
    #             # mapped_VPA_length_dist[fromNode] = (length, path)
    #             toNode = dict_edges[val2[0]][1]
    #             length, path = nx.single_source_dijkstra(G, toNode)
    #             # mapped_VPA_length_dist[toNode] = (length, path)
    #
    # end_time = time.time()
    # print "Calculation duration:", str(end_time - start_time)


    # def compute_NP_ALL(VPA_ID, Route):
    #     service_time = time.time()
    #     tokensForEdgedRoute = Route.split(' ')
    #     edgedRoute = []
    #     for j, val2 in enumerate(tokensForEdgedRoute):
    #         edgedRoute.append(val2)
    #     nodedRoute = nodesOfEdgedRoute(dict_edges, edgedRoute, WithFirstNode = False)
    #     nearestNodes, dist, path = nearestNodeToVPA_dist_path(G, dict_edges, mapped_VPA[int(VPA_ID)],mapped_Type_VPA[int(VPA_ID)], mapped_VPA_length_dist,nodedRoute)
    #     reversedPath = path[::-1]
    #     edge_to_NP = " "
    #     edge_from_NP = " "
    #     for j, val2 in enumerate(edgedRoute):
    #         if edge_to_NP != " " and edge_from_NP != " ":
    #             break
    #         if dict_edges[val2][0] == nearestNodes[1]:
    #             edge_from_NP = val2.decode().encode('utf-8')
    #         if dict_edges[val2][1] == nearestNodes[1]:
    #             edge_to_NP = val2.decode().encode('utf-8')
    #     edgesOfNP = edgesOfNearestPoint(edgedRoute, nearestNodes[1], dict_edges)
    #     edgedRoute_NP_VPA, dist_NP_VPA = edgesOfNodedRoute(G, reversedPath, shortest=True)
    #     if (dist_NP_VPA != dist):
    #         print "Distance in the 2 direction are not the same\n"
    #     # reversedPath.reverse()
    #     service_time = time.time() - service_time
    #     print "[VPA_NODE,NP_NODE]", str(nearestNodes), "[Edge->NP, NP->Edge]", edgesOfNP, "[Dist_NP_VPA]", str(
    #         dist), "[Route_NP_VPA]", str(edgedRoute_NP_VPA), "Service duration", service_time, "\n"
    #     route_as_string = ""
    #     for i, val in enumerate(edgedRoute_NP_VPA):
    #         if i == 0:
    #             route_as_string = val.decode().encode('utf-8')
    #         else:
    #             route_as_string = route_as_string + " " + val.decode().encode('utf-8')
    #     if edgedRoute_NP_VPA == []:
    #         route_as_string = " "
    #     msg = [str(constx.RESPONSE),str(constx.RESPONSE_NP_ALL),str(constx.EDGE_TO_NP),str(edgesOfNP[0]), str(constx.NODE_NP),str(nearestNodes[1]), str(constx.EDGE_FROM_NP),str(edgesOfNP[1]) , str(constx.NODE_VPA_MAPPING),str(nearestNodes[0]), str(constx.ROUTE_NP_VPA),str(route_as_string), str(constx.ROUTE_LENGTH_NP_VPA),str(float(dist_NP_VPA))]
    #     msg_as_string = ""
    #     for j in xrange(0, len(msg), 2):
    #         msg_as_string = msg_as_string + msg[j].decode().encode('utf-8') + ":" + msg[j + 1].decode().encode('utf-8')
    #         if j == len(msg)-2:
    #             msg_as_string = msg_as_string+"#"
    #         else:
    #             msg_as_string = msg_as_string + ";"
    #     return msg_as_string
    #
    # def compute_EDGE_BEST_TRAVEL_TIME(EDGE_ID):
    #     travelTime = sys.maxint
    #     service_time = time.time()
    #     nodesOfEdge = ("","")
    #     nodesOfEdge = dict_edges[EDGE_ID]
    #     if (nodesOfEdge != ("","")) and (G.has_edge(nodesOfEdge[0],nodesOfEdge[1])):
    #         edges = G[nodesOfEdge[0]][nodesOfEdge[1]]
    #         for j, val in edges.iteritems():
    #             if val["label"] == EDGE_ID:
    #                 if val["maxSpeed"] != 0.0:
    #                     travelTime = val["weight"] / val["maxSpeed"]
    #                 else:
    #                     raise ValueError("Edge Max Speed value equals 0.0")
    #     else:
    #         raise ValueError("Edge not found")
    #     service_time = time.time() - service_time
    #     print "[EDGE_ID]", str(EDGE_ID), "[EDGE_BEST_TRAVEL_TIME]", str(travelTime), "\n"
    #     msg = [str(constx.RESPONSE),str(constx.RESPONSE_EDGE_BEST_TRAVEL_TIME),str(constx.EDGE_BEST_TRAVEL_TIME),str(float(travelTime))]
    #     msg_as_string = ""
    #     for j in xrange(0, len(msg), 2):
    #         msg_as_string = msg_as_string + msg[j].decode().encode('utf-8') + ":" + msg[j + 1].decode().encode('utf-8')
    #         if j == len(msg)-2:
    #             msg_as_string = msg_as_string+"#"
    #         else:
    #             msg_as_string = msg_as_string + ";"
    #     return msg_as_string

#    sys.stdout = open("PyServerLog.txt", "w")



    # CONNECTION_LIST = []  # list of socket clients
    #
    #
    # # Add server socket to the list of readable connections
    # CONNECTION_LIST.append(server_socket)
    #
    # while 1:
    #     # Get the list sockets which are ready to be read through select
    #     read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [])
    #
    #     for sock in read_sockets:
    #
    #         # New connection
    #         if sock == server_socket:
    #             # Handle the case in which there is a new connection recieved through server_socket
    #             sockfd, addr = server_socket.accept()
    #             CONNECTION_LIST.append(sockfd)
    #             print "Client (%s, %s) connected" % addr
    #
    #         # Some incoming message from a client
    #         else:
    #             # Data recieved from client, process it
    #             try:
    #                 # In Windows, sometimes when a TCP program closes abruptly,
    #                 # a "Connection reset by peer" exception will be thrown
    #                 data = sock.recv(RECV_BUFFER)
    #                 if data == "CLOSE":
    #                     print "Client (%s, %s) is going offline" % addr
    #                     sock.close()
    #                     CONNECTION_LIST.remove(sock)
    #                     continue
    #                 tmp_str = data
    #                 tokens = tmp_str.split('#')
    #                 for i, val in enumerate(tokens):
    #                     if val == "":
    #                         continue
    #                     tokens_msg = val.split(';')
    #                     # for j, val2 in enumerate(tokens_msg):
    #                     tokens_command = tokens_msg[0].split(':')
    #                     msg_type = int(tokens_command[0])
    #                     cmd = int(tokens_command[1])
    #                     tokens_args = []
    #                     for j, val2 in enumerate(tokens_msg[1:]):
    #                         tmp = val2.split(':')
    #                         tokens_args.append(int(tmp[0]))
    #                         tokens_args.append(tmp[1])
    #                     if msg_type == constx.QUERY:
    #                         if cmd in constx.KNOWN_QUERIES:
    #                             cmd_format = constx.FORMAT_QUERIES[cmd]
    #                             error = False
    #                             if len(tokens_args) != len(cmd_format):
    #                                 error = True
    #                                 for j in xrange(2, len(tokens_args), 2):
    #                                     if tokens_msg[j] != cmd_format[j]:
    #                                         error = True
    #                             if error:
    #                                 raise ValueError("Error query format")
    #                             if cmd == constx.CMD_NP_ALL:
    #                                 response_msg = compute_NP_ALL(tokens_args[1], tokens_args[3])
    #                                 sock.send(response_msg)
    #                             elif cmd == constx.CMD_EDGE_BEST_TRAVEL_TIME:
    #                                 response_msg = compute_EDGE_BEST_TRAVEL_TIME(tokens_args[1])
    #                                 sock.send(response_msg)
    #                     elif msg_type == constx.RESPONSE:
    #                         print "Not supported for now"
    #                     else:
    #                         raise ValueError("unrecognazible msg type received")
    #
    #             # client disconnected, so remove from socket list
    #             except:
    #                 print "Client (%s, %s) is offline" % addr
    #                 sock.close()
    #                 CONNECTION_LIST.remove(sock)
    #                 continue
    #
    # server_socket.close()

    # conn, addr = server_socket.accept()
    # while True:
    #     print 'Connected by client', addr
    #     data = conn.recv(4096)
    #     if not data:
    #         print ("no data")
    #     else:
    #         print 'Received data from client', data
    #         if data == "CLOSE":
    #             conn.close()
    #         else:
    #             tmp_str=data
    #             tokens = tmp_str.split('#')
    #             for i, val in enumerate(tokens):
    #                 if val == "":
    #                     continue
    #                 tokens_msg = val.split(';')
    #                 # for j, val2 in enumerate(tokens_msg):
    #                 tokens_command = tokens_msg[0].split(':')
    #                 msg_type = int(tokens_command[0])
    #                 cmd = int(tokens_command[1])
    #                 tokens_args =[]
    #                 for j, val2 in enumerate(tokens_msg[1:]):
    #                     tmp = val2.split(':')
    #                     tokens_args.append(int(tmp[0]))
    #                     tokens_args.append(tmp[1])
    #                 if msg_type == constx.QUERY:
    #                     if cmd in constx.KNOWN_QUERIES:
    #                         cmd_format = constx.FORMAT_QUERIES[cmd]
    #                         error = False
    #                         if len(tokens_args) != len(cmd_format):
    #                             error = True
    #                             for j in xrange(2, len(tokens_args),2):
    #                                 if tokens_msg[j] != cmd_format[j]:
    #                                     error = True
    #                         if error:
    #                             raise ValueError("Error query format")
    #                         if cmd == constx.CMD_NP_ALL:
    #                             response_msg = compute_NP_ALL(tokens_args[1], tokens_args[3])
    #                             conn.send(response_msg)
    #                         elif cmd == constx.CMD_EDGE_BEST_TRAVEL_TIME:
    #                             response_msg = compute_EDGE_BEST_TRAVEL_TIME(tokens_args[1])
    #                             conn.send(response_msg)
    #                 elif msg_type == constx.RESPONSE:
    #                     print "Not supported for now"
    #                 else:
    #                     raise ValueError("unrecognazible msg type received")
    #             # cmd_args = cmd.split(';')
    #             # nbrArgs = len(cmd_args)
    #             # print "nbr arguments", nbrArgs
    #             # cmdID = cmd_args[0]
    #             # print "command ID", cmdID
    #             # # dist = dijkstraPathLength(G, cmd_args[1], cmd_args[2])
    #             # # conn.send("Shortest distance between:"+str(cmd_args[1])+"&"+str(cmd_args[2])+"="+str(dist)+"\n")
    #             # # conn.send('Thank you for connecting\n')
    #             # vpa_index = cmd_args[1]
    #             # tokensForEdgedRoute = cmd_args[2].split(' ')
    #             # edgedRoute = []
    #             # for j, val2 in enumerate(tokensForEdgedRoute):
    #             #     edgedRoute.append(val2)
    #             # nodedRoute = nodesOfEdgedRoute(dict_edges, edgedRoute)
    #             # nearestNodes, dist, path = nearestNodeToVPA_dist_path(G, dict_edges, mapped_VPA[int(vpa_index)], mapped_Type_VPA[int(vpa_index)], mapped_VPA_length_dist, nodedRoute)
    #             # # nearestNodes, dist = nearestNodeToVPA(G, dict_edges, mapped_VPA[int(vpa_index)], mapped_Type_VPA[int(vpa_index)], nodedRoute)
    #             # service_time = time.time() - service_time
    #             # reversedPath = path[::-1]
    #             # edge_to_NP = ""
    #             # edge_from_NP = ""
    #             # for j, val2 in enumerate(edgedRoute):
    #             #     if edge_to_NP != "" and edge_from_NP != "":
    #             #         break
    #             #     if dict_edges[val2][0] == nearestNodes[1]:
    #             #         edge_from_NP = val2.decode().encode('utf-8')
    #             #     if dict_edges[val2][1] == nearestNodes[1]:
    #             #         edge_to_NP = val2.decode().encode('utf-8')
    #             # edgesOfNP = edgesOfNearestPoint(edgedRoute, nearestNodes[1], dict_edges)
    #             # edgedRoute_NP_VPA, dist_NP_VPA = edgesOfNodedRoute(G, reversedPath, shortest=True)
    #             # if (dist_NP_VPA != dist):
    #             #     print "Distance in the 2 direction are not the same\n"
    #             # # reversedPath.reverse()
    #             # print "[VPA_NODE,NP_NODE]", str(nearestNodes), "[Edge->NP, NP->Edge]", edgesOfNP,"[Dist_NP_VPA]", str(dist),"[Route_NP_VPA]", str(edgedRoute_NP_VPA) ,"Service duration", service_time,"\n"
    #             # route_as_string = ""
    #             # for i, val in enumerate(edgedRoute_NP_VPA):
    #             #     if i == 0:
    #             #         route_as_string = val.decode().encode('utf-8')
    #             #     else:
    #             #         route_as_string = route_as_string+" "+val.decode().encode('utf-8')
    #             # # conn.send("[VPA_NODE]:"+str(nearestNodes[0])+";[NP_NODE]:"+str(nearestNodes[1])+";[NP_EdgeTo]:"+str(edgesOfNP[0])+";[NP_EdgeFm]:"+str(edgesOfNP[1])+";[Dist_NP_VPA]:"+str(dist)+";[Route_NP_VPA]:"+str(edgedRoute_NP_VPA))
    #             # service_time = time.time() - service_time
    #             # conn.send("[VPA_NODE]:" + str(nearestNodes[0]) + ";[NP_NODE]:" + str(nearestNodes[1]) + ";[NP_EdgeTo]:" + str(edgesOfNP[0]) + ";[NP_EdgeFm]:" + str(edgesOfNP[1]) + ";[Dist_NP_VPA]:" + str(dist) + ";[Route_NP_VPA]:" + str(route_as_string))
    #             # conn.send("Shortest distance between:" + str(nearestNodes[0]) + "&" + str(nearestNodes[1]) + "=" + str(dist) + ":"+ str(edgedRoute_NP_VPA) +"NP Edges:"+ str(edgesOfNP) +";")
    #             # conn.send('Thank you for connecting\n')

        # conn.close()
if __name__ == "__main__":
    main(sys.argv)

