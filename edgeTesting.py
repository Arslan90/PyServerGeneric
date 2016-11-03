import os
import sys


import subprocess
PORT = 10002
sumoBinary = "/usr/local/bin/sumo"
sumoProcess = subprocess.Popen([sumoBinary, "-c", "/media/DATA/DoctoratTlemcen/Git/mixim/mixim/examples/veins/gridGeoDTN/noTraci.sumo.cfg", "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)

import traci
import traci.constants as tc
traci.init(PORT)
step = 0

listEdges = traci.edge.getIDList()
while step < 7200:
    for i, val in enumerate(listEdges):
        as_str = val
        if as_str[0] == ":":
            continue
        # currentTravelTime = traci.edge.getTraveltime(val)
        # if (currentTravelTime > 100):
        #     print "Time:", str(step), "EdgeID:", str(val), "TravelTime:", str(currentTravelTime),"s\n"
        # lastStepMeanSpeed = traci.edge.getLastStepMeanSpeed(val)
        # if (lastStepMeanSpeed == 0):
        #     print "Time:", str(step), "EdgeID:", str(val), "lastStepMeanSpeed:", str(lastStepMeanSpeed), "s\n"


        lastStepMeanSpeed = traci.edge.getLastStepMeanSpeed(val)

        lastStepVehicleIDs = traci.edge.getLastStepVehicleIDs(val)

        print str(lastStepMeanSpeed)
        print str(lastStepVehicleIDs)
        # print "Time:", str(step), "EdgeID:", str(val), "lastStepMeanSpeed:", str(lastStepMeanSpeed), "s\n"
        # if (lastStepMeanSpeed == 0.0):
        #     lastStepMeanSpeed = 13.9
        #     currentTravelTime = 140 / lastStepMeanSpeed
        # else:
        #     currentTravelTime = traci.edge.getTraveltime(val)
        # # print "Time:", str(step), "EdgeID:", str(val), "TravelTime:", str(currentTravelTime), "s\n"
        #
        # if (currentTravelTime > 20):
        #     print "Time:", str(step), "EdgeID:", str(val), "TravelTime:", str(currentTravelTime),"s\n"

    traci.simulationStep()
    step += 1
traci.close()