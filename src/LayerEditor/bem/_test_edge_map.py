from side_project_map import SideProjectMapping
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d
from matplotlib import collections
import math
import random

def inside_web(n, poly, epsilon, n_subdiv):
    poly = [ np.array(p) for p in poly ]
    points = []
    for i in range(len(poly)):
        t0 = poly[i-2] - poly[i-1]
        t0 = t0 / np.linalg.norm(t0)
        t1 = poly[i] - poly[i-1]
        t1 = t1 / np.linalg.norm(t1)
        n0 = np.array([t0[1], -t0[0]])
        n1 = np.array([-t1[1], t1[0]])
        n01 = n0 + n1
        a = epsilon / n01.dot(n0)
        X = poly[i-1] + a * n01
        points.append(X)
    subdiv_points=[]
    for B, A in zip(points, rotate(points)):
        dB = (B - A) / n_subdiv
        for i in range(n_subdiv):
            X = A + i * dB
            subdiv_points.append( (X[0], X[1]) )
    return subdiv_points


def perturb_points(points):
    perturbed=[]
    for (x, y) in points:
        ix = random.gauss(0.2, 0.2)
        iy = random.gauss(0.2, 0.2)
        perturbed.append(  (x+ix,  y+iy) )
    return perturbed


def make_polygon(n_sides, phase=0.0):
    points=[]
    a=phase
    inc=2*math.pi / n_sides
    for i in range(n_sides):
        x= math.cos(a)
        y= math.sin(a)
        points.append( (x,y) )
        a+=inc
    return points


def random_inside_points(n, poly):
    points=[]
    while len(points) < n:
        r = random.uniform(0, 1)
        angle = random.uniform(0, 2*math.pi)
        X=(r*math.cos(angle), r*math.sin(angle))
        last_corner = poly[-1]
        for corner in poly:
            r=(corner[0]-last_corner[0], corner[1] - last_corner[1])
            d=cross2d(corner, r)
            if cross2d(X, r) > d:
                break
            last_corner=corner
        else:
            points.append(X)
    return points



def plot_poly(poly, color, style = 'o-'):
    points = poly + [poly[0]]
    x,y= zip(*points)
    ax.plot(x,y, style, color = color)

def map_poly(poly_in, poly_out):
    #fill_in = inside_web(20, poly_in, 0.0001, 6)
    fill_in = inside_web(20, poly_in, 0.05, 6)
    #fill_in += inside_web(20, poly_in, 0.1, 6)
    mp = MapPoints(poly_in, poly_out, (0.0, 1.0))
    fill_out = mp.map_points(fill_in)
    #mp.plot_def_and_tractions()
    return (poly_in, poly_out, fill_in, fill_out)


n_edges=8
edges=[]
dist_edges=[]
h=0.1
for i in range(n_edges):
    a = (random.uniform(0,1), random.uniform(0,1) )
    b = (random.uniform(0, 1), random.uniform(0, 1))
    edges.append( (a,b) )
    da = ( a[0] + random.uniform(-h,  h), a[1] + random.uniform(-h, h))
    db = ( b[0] + random.uniform(-h,  h), b[1] + random.uniform(-h, h))
    dist_edges.append( (da,db) )

n_points=10
points=[]
for i in range(n_points):
    points.append( (random.uniform(0,1), random.uniform(0,1) ) )


"""
edges = [[(0,-1), (0,1)], [ (1,-1), (1,1)], [(-1,-1), (-1,1)]]
dist_edges=[]
for a,b in edges:
    da = (a[0] + random.uniform(-h, h), a[1] + random.uniform(-h, h))
    db = (b[0] + random.uniform(-h, h), b[1] + random.uniform(-h, h))
    dist_edges.append((da, db))
"""

#e=0.01
#points=[(0+e,0.5), (0-e,0.5), (0+e,-0.5), (0-e,-0.5)]

nx, ny = (10, 10)
x = np.linspace(0, 1, nx)
y = np.linspace(0, 1, ny)
xv, yv = np.meshgrid(x, y)
points = list(zip(xv.flatten(), yv.flatten()))

fig, ax = plt.subplots()

spm = SideProjectMapping(edges, dist_edges)
dist_points = spm.map_points(points)


lc1=collections.LineCollection(edges, color='g')
ax.add_collection(lc1)

lc2=collections.LineCollection(dist_edges, color='r')
ax.add_collection(lc2)

X, Y = zip(*points)
#ax.plot(X,Y, 'o', color='b')

dX, dY = zip(*dist_points)
U = np.array(dX) - np.array(X)
V = np.array(dY) - np.array(Y)
ax.quiver(X, Y, U, V, angles='xy', scale_units='xy', scale=1, color='m')

ax.autoscale()
ax.margins(0.5)

plt.show()






