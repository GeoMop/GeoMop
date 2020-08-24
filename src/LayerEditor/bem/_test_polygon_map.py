
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


fig, ax = plt.subplots()
#random.seed(a=123)

poly_orig = make_polygon(7)

#poly_orig = [(0,0), (1,0), (1,1), (0,1)]


# linear transform - constant tension
transform = np.array([[1.2, 1.0], [0, 1.4]])
#poly_def = np.dot( np.array(poly_orig), transform)
#poly_def = [ (x,y) for (x,y) in poly_def]

poly_def = perturb_points(poly_orig)

# map points def -> orig
#poly_in, poly_out, fill_in, fill_out = map_poly(poly_def, poly_orig)

# map points orig -> def
poly_in, poly_out, fill_in, fill_out = map_poly(poly_orig, poly_def)

#fill_in = np.dot( np.array(fill_in), transform)
#fill_in = [ (x,y) for (x,y) in fill_in]

plot_poly(poly_in, 'green')
plot_poly(poly_out, 'red')

# points
plot_poly(fill_in, 'limegreen')
#x, y = zip(*inside)
#ax.plot(x, y, 'b-')

# maped points
plot_poly(fill_out, 'orangered')
#x, y = zip(*orig_inside)
#ax.plot(x, y, 'm-')

plt.axis('equal')
ax.set_xlim([-2, 2])
ax.set_ylim([-2, 2])

plt.show()

# TODO:
# debug BEM code, why only one mapped side is a curve?
