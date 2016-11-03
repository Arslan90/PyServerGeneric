import os
import sys
#if 'SUMO_HOME' in os.environ:
#    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
#    sys.path.append(tools)
#else:
#    sys.exit("please declare environment variable 'SUMO_HOME'")
import sumolib
#net = sumolib.net.readNet('/media/DATA/DoctoratTlemcen/SIM_Tools_Arslan/sumo-0.13.1/tools/smallGrid.net.xml')
#print net.getNode('1/1').getCoord()
#print net.getNodes()
#for Node in  net.getNodes():
#    print Node.getID()
#    print Node.getCoord()
#net = sumolib.net.readNet('/media/DATA/DoctoratTlemcen/Git/mixim/mixim/examples/veins/cologne2H/cologne.net.xml')
net = sumolib.net.readNet('/media/WIN7/Users/Arslan/Downloads/Compressed/TAPASCologne-0.24.0/TAPASCologne-0.24.0/cologne2.net.xml')
print len(net.getNodes())
for Node in  net.getNodes():
    print Node.getID()
    print Node.getCoord()
