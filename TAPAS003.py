import os
import sys
import sumolib

#net = sumolib.net.readNet()
#print net.getNode('1/1').getCoord()
#print net.getNodes()
#for Node in  net.getNodes():
#    print Node.getID()
#    print Node.getCoord()
net = sumolib.net.readNet('/media/DATA/DoctoratTlemcen/Git/mixim/mixim/examples/veins/cologne2H/cologne_modified.net.xml')
# net = sumolib.net.readNet('/media/DATA/DoctoratTlemcen/Git/mixim/mixim/examples/veins/gridGeoDTN/grid_9x9.net.xml')
#net = sumolib.net.readNet('/media/DATA/DoctoratTlemcen/Git/mixim/mixim/examples/veins/cologne2H/cologne.net.xml')
#net = sumolib.net.readNet('/media/DATA/DoctoratTlemcen/SIM_Tools_Arslan/sumo-0.13.1/tools/smallGrid.net.xml')
#net = sumolib.net.readNet('/media/WIN7/Users/Arslan/Downloads/Compressed/TAPASCologne-0.24.0/TAPASCologne-0.24.0/cologne2.net.xml')
#net = sumolib.net.readNet('/media/DATA/DoctoratTlemcen/Experimentations/petite2H_Nothing/noTraCI.sumo.cfg')
#net = sumolib.net.readNet('/media/DATA/DoctoratTlemcen/Experimentations/petite2H_Nothing/petitprophet.net.xml')

#with open("./graph.txt", "w") as myFile:

myFile = open("graph_cologne3.txt", "w")
# myFile = open("graph_test.txt", "w")

print "Total Number of nodes: ", len(net.getNodes())
myFile.write("Total Number of nodes: "+str(len(net.getNodes()))+"\n")
print "[Nodes Section]"
myFile.write("[Nodes Section]\n")
for Node in  net.getNodes():
     # print "ID: ", Node._id,
     # print "Coord: ", Node._coord,
     # print ""
     myFile.write("ID: "+ str(Node._id)+" Coord: "+str(Node._coord)+"\n")
print "[Edges Section]"
myFile.write("[Edges Section]\n")
for Edge in net.getEdges():
     # print "ID: ", Edge.getID(),
     # print "Name: ", Edge.getName(),
     # print ""
     # print "Outgoing nodes",
     # print "From: ", Edge._from._id,
     # print "Incoming nodes",
     # print "To: ", Edge._to._id,
     # print ""
     print "MaxSpeed: ", Edge.getSpeed(),
     myFile.write("ID: "+ str(Edge.getID())+" From: "+str(Edge._from._id)+" To: "+str(Edge._to._id)+" Length: "+str(Edge.getLength())+" MaxSpeed: "+str(Edge.getSpeed())+"\n")

myFile.close()
