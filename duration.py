import math
import operator

omnetFile = open("duration.txt", "r")
f_line = omnetFile.readline()
duration = 0.0
my_list = []
while f_line <> "":
    print f_line
    tokens = f_line.split(":")
    duration+= float(tokens[1])
    my_list.append(float(tokens[1]))
    f_line = omnetFile.readline()
print "Total duration:", duration
#my_list = sorted(my_list, key=operator.itemgetter(1))
print "List:", sorted(my_list, reverse=True)
