This directory is a example of scenario handled by the PyServer

1) Considered scenario: cologne(TAPAS003)
2) Example of command line:
(MyPC): ProdServerGeneric.py -i /media/DATA/DoctoratTlemcen/Git/mixim/mixim/examples/veins/cologne2HGeoDTN/cologne.net.xml -x cologneTAPAS003/cologne_SpecialBuild.txt -b [(0,0);(34288.8,41946.86)] -r 127 -c /media/DATA/DoctoratTlemcen/Git/mixim/mixim/examples/veins/cologne2HGeoDTN/cologneGeoDTN.omnetpp.ini

NOTE: cologne.net.xml is not compatible with sumolib 0.13 due to the use of attribute speed instead of maxSpeed (easily fixed by replacing speed by maxSpeed in cologne.net.xml)