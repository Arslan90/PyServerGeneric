import math

def dot(v,w):
    # x,y,z = v
    # X,Y,Z = w
    # return x*X + y*Y + z*Z
    return v[0]*w[0]+v[1]*w[1]

def length(v):
    # x,y,z = v
    # return math.sqrt(x*x + y*y + z*z)
    return math.sqrt(float(v[0])**2+float(v[1])**2)

def vector(b,e):
    # x,y,z = b
    # X,Y,Z = e
    # return (X-x, Y-y, Z-z)
    return (e[0]-b[0],e[1]-b[1])

def unit(v):
    # x,y,z = v
    # mag = length(v)
    # return (x/mag, y/mag, z/mag)
    mag = length(v)
    return (v[0]/mag, v[1]/mag)

def distance(p0,p1):
    return length(vector(p0,p1))

def scale(v,sc):
    # x,y,z = v
    # return (x * sc, y * sc, z * sc)
    return (v[0] * sc, v[1] * sc)

def add(v,w):
    # x,y,z = v
    # X,Y,Z = w
    # return (x+X, y+Y, z+Z)
    return (v[0]+w[0],v[1]+w[1])

def pnt2line(pnt, start, end):
    line_vec = vector(start, end)
    pnt_vec = vector(start, pnt)
    line_len = length(line_vec)
    line_unitvec = unit(line_vec)
    pnt_vec_scaled = scale(pnt_vec, 1.0/line_len)
    t = dot(line_unitvec, pnt_vec_scaled)
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    nearest = scale(line_vec, t)
    dist = distance(nearest, pnt_vec)
    nearest = add(nearest, start)
    return nearest, dist
