import os
import sys
import math
import vectors

# def dot(v,w):
#     # x,y,z = v
#     # X,Y,Z = w
#     # return x*X + y*Y + z*Z
#     return v[0]*w[0]+v[1]*w[1]
#
# def length(v):
#     # x,y,z = v
#     # return math.sqrt(x*x + y*y + z*z)
#     return math.sqrt(float(v[0])**2+float(v[1])**2)
#
# def vector(b,e):
#     # x,y,z = b
#     # X,Y,Z = e
#     # return (X-x, Y-y, Z-z)
#     return (e[0]-b[0],e[1]-b[1])
#
# def unit(v):
#     # x,y,z = v
#     # mag = length(v)
#     # return (x/mag, y/mag, z/mag)
#     mag = length(v)
#     return (v[0]/mag, v[1]/mag)
#
# def distance(p0,p1):
#     return length(vector(p0,p1))
#
# def scale(v,sc):
#     # x,y,z = v
#     # return (x * sc, y * sc, z * sc)
#     return (v[0] * sc, v[1] * sc)
#
# def add(v,w):
#     # x,y,z = v
#     # X,Y,Z = w
#     # return (x+X, y+Y, z+Z)
#     return (v[0]+w[0],v[1]+w[1])
#
# def pnt2line(pnt, start, end):
#     line_vec = vector(start, end)
#     pnt_vec = vector(start, pnt)
#     line_len = length(line_vec)
#     line_unitvec = unit(line_vec)
#     pnt_vec_scaled = scale(pnt_vec, 1.0/line_len)
#     t = dot(line_unitvec, pnt_vec_scaled)
#     if t < 0.0:
#         t = 0.0
#     elif t > 1.0:
#         t = 1.0
#     nearest = scale(line_vec, t)
#     dist = distance(nearest, pnt_vec)
#     nearest = add(nearest, start)
#     return nearest, dist

def node_inside_circle(x, y, circle_x, circle_y, r):
    sqr_dist = -1
    sqr_dist = (x - circle_x)**2 + (y - circle_y)**2
    if sqr_dist <= r**2:
        return True, math.sqrt(sqr_dist)
    else:
        return False, sqr_dist

def edge_inside_circle(x1, y1, x2, y2, circle_x, circle_y, r):
    near_dist = -1
    start = (float(x1), float(y1))
    end = (float(x2), float(y2))
    pnt = (float(circle_x), float(circle_y))
    near_coord, near_dist = vectors.pnt2line(pnt,start,end)
    if near_dist <= r:
        return True, near_dist
    else:
        return False, near_dist

netBound1 = (0,0)
netBound2 = (34288.8,41946.86)
margin = 0

def sumo2omnet(sumo_x,sumo_y):
    omnet_x = sumo_x - netBound1[0] + margin
    omnet_y = (netBound2[1] - netBound1[1]) - (sumo_y - netBound1[1]) + margin
    return omnet_x, omnet_y

def omnet2sumo(omnet_x,omnet_y):
    sumo_x = omnet_x + netBound1[0] + margin
    sumo_y = (netBound2[1] - netBound1[1]) - (omnet_y - netBound1[1]) + margin
    return sumo_x, sumo_y

#############################################################

###################### Main programm ########################

#############################################################
myFile = open("TAPAS_VPA.txt", "r")

index = 0
sumo_VPA = []
omnet_VPA = []

while True:
    line1 = myFile.readline()
    if not line1: break  # EOF
    tokens = line1.split('.')
    x_string = tokens[2].split('=')
    x_string = x_string[1].replace(" ","")
    x_string = x_string.rstrip()
    x = float(x_string)
    line2 = myFile.readline()
    if not line2: break  # EOF
    tokens = line2.split('.')
    y_string = tokens[2].split('=')
    y_string = y_string[1].replace(" ","")
    y_string = y_string.rstrip()
    y = float(y_string)
    sumo_x, sumo_y = omnet2sumo(x,y)
    omnet_VPA.append((x,y))
    sumo_VPA.append((sumo_x,sumo_y))
    print "\nVPA Index:", index, "Omnet_Coord:", x,";", y, "Sumo_Coord:", sumo_x, ";", sumo_y
    index +=1

index = 0
sumo_nodes_dict = {}
sumo_nodes = []
myFile = open("nodes.txt", "r")
f_line = myFile.readline()
while f_line <> "":
    tokens = f_line.split(' ')
    id = tokens[1]
    x_coord = tokens[3].translate(None, '[,')
    y_coord = tokens[4].translate(None, ']')
    y_coord = y_coord.rstrip()
    sumo_nodes.append((id, (x_coord, y_coord)))
    sumo_nodes_dict[id] = index
    index +=1
    f_line = myFile.readline()
myFile.close()

sumo_edges = []
myFile = open("edges.txt", "r")
f_line = myFile.readline()
while f_line <> "":
    tokens = f_line.split(' ')
    id = tokens[1]
    from_node = tokens[3]
    to_node = tokens[5]
    edge_length = tokens[7]
    from_index = sumo_nodes_dict[from_node]
    to_index = sumo_nodes_dict[to_node]
    sumo_edges.append((id, sumo_nodes[from_index][1][0], sumo_nodes[from_index][1][1], sumo_nodes[to_index][1][0], sumo_nodes[to_index][1][1]))
    f_line = myFile.readline()
myFile.close()

# for i, val in enumerate(sumo_edges):
#     print val

# for i, val in enumerate(sumo_nodes_dict):
#     print i, str(val)

# for x in sumo_nodes_dict:
#     print (x), ":", sumo_nodes_dict[x]
    # for y in sumo_nodes_dict[x]:
    #     print (y,':',sumo_nodes_dict[x][y])

vpa_nodes_map = []
radio_range = 300
print "radio_range:", radio_range

nbr_not_mapped_to_node = 0

for i,val in enumerate(sumo_VPA[:50]):
    map = []
    for j, val2 in enumerate(sumo_nodes):
        result = False
        dist = -1
        result, dist = node_inside_circle(float(val2[1][0]), float(val2[1][1]), float(val[0]), float(val[1]), radio_range)
        if result == True:
            map.append((val2[0],dist))
    if map == []:
        nbr_not_mapped_to_node +=1
    vpa_nodes_map.append(map)

print "nbr not mapped to node:", nbr_not_mapped_to_node

nbr_not_mapped_to_edge = 0

for i,val in enumerate(vpa_nodes_map):
    if val != []:
        continue
    map = []
    for j, val2 in enumerate(sumo_edges):
        result = False
        dist = -1
        result, dist = edge_inside_circle(float(val2[1]), float(val2[2]), float(val2[3]), float(val2[4]), float(sumo_VPA[i][0]), float(sumo_VPA[i][1]), radio_range)
        if result == True:
            map.append((val2[0],dist))
    if map == []:
        nbr_not_mapped_to_edge +=1
    vpa_nodes_map[i] = map

print "nbr not mapped to edge:", nbr_not_mapped_to_edge

for i,val in enumerate(vpa_nodes_map):
    if val == []:
        print i, sumo_VPA[i][0], sumo_VPA[i][1]


# index_not_mapped_to_node = []
#
# for i, val in enumerate(vpa_nodes_map):
#     if val == []:
#         index_not_mapped_to_node.append(i)
#         nbr_not_mapped_to_node +=1
#     print i, val





# radius = 20
# print "radius:", radius
#
# for i,val in enumerate(sumo_VPA):
#     map = []
#     for j, val2 in enumerate(sumo_nodes):
#         result = False
#         dist = -1
#         result, dist = inside_circle(float(val[0]), float(val[1]), float(val2[1][0]), float(val2[1][1]), radius)
#         if result == True:
#             map.append((val2[0],dist))
#     vpa_nodes_map.append(map)
#
# for i, val in enumerate(vpa_nodes_map):
#     print i, val
#
# radius = 50
# print "radius:", radius
#
# for i,val in enumerate(sumo_VPA):
#     map = []
#     if vpa_nodes_map[i] != []:
#         continue
#     else:
#         for j, val2 in enumerate(sumo_nodes):
#             result = False
#             dist = -1
#             result, dist = inside_circle(float(val[0]), float(val[1]), float(val2[1][0]), float(val2[1][1]), radius)
#             if result == True:
#                 map.append((val2[0],dist))
#         vpa_nodes_map[i]= map
#
# # for i, val in enumerate(vpa_nodes_map):
# #     print i, val
#
# radius = 100
# print "radius:", radius
#
# for i,val in enumerate(sumo_VPA):
#     map = []
#     if vpa_nodes_map[i] != []:
#         continue
#     else:
#         for j, val2 in enumerate(sumo_nodes):
#             result = False
#             dist = -1
#             result, dist = inside_circle(float(val[0]), float(val[1]), float(val2[1][0]), float(val2[1][1]), radius)
#             if result == True:
#                 map.append((val2[0],dist))
#         vpa_nodes_map[i]= map
#
# # for i, val in enumerate(vpa_nodes_map):
# #     print i, val
#
# radius = 200
# print "radius:", radius
#
# for i, val in enumerate(sumo_VPA):
#     map = []
#     if vpa_nodes_map[i] != []:
#         continue
#     else:
#         for j, val2 in enumerate(sumo_nodes):
#             result = False
#             dist = -1
#             result, dist = inside_circle(float(val[0]), float(val[1]), float(val2[1][0]), float(val2[1][1]), radius)
#             if result == True:
#                 map.append((val2[0], dist))
#         vpa_nodes_map[i] = map
#
# # for i, val in enumerate(vpa_nodes_map):
# #     print i, val
#
# radius = 500
# print "radius:", radius
#
# for i, val in enumerate(sumo_VPA):
#     map = []
#     if vpa_nodes_map[i] != []:
#         continue
#     else:
#         for j, val2 in enumerate(sumo_nodes):
#             result = False
#             dist = -1
#             result, dist = inside_circle(float(val[0]), float(val[1]), float(val2[1][0]), float(val2[1][1]), radius)
#             if result == True:
#                 map.append((val2[0], dist))
#         vpa_nodes_map[i] = map
#
# for i, val in enumerate(vpa_nodes_map):
#     print i, val
