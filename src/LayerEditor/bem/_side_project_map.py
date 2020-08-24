import numpy as np
import matplotlib.pyplot as plt

class SideProjectMapping:
    """
    Class to define mapping through displacement of set of edges.
    The mapping is defined by a set of edges 'orig_edges' and set of moved edges 'new_edges'.
    Than a set of points may be mapped using the map_points or map_point functions.

    The mapping should have following properties:
    - points on original edges are mapped to corresponding points on new edges (do not hold on intersection of edges).
    - if the edges forms a decomposition of the plane to (nonconvex) polygons, the points inside old polygons are mapped to ppoints in new polygons.
    - the mapping is continuous
    - mapping is smooth inside polygons

    Mapping of point P is weighted average of its projections to individual edges. Weights are 1/r^2 where 'r' is the distances to the projection.
    """

    def __init__(self, orig_edges, new_edges):
        """
        :param orig_edges: Initial set of edges.
        :param new_edges: Set of  displaced edges (same number of edges).
        """
        assert (len(orig_edges) == len(new_edges))
        self.displ = np.array(new_edges) - np.array(orig_edges)
        self.edges = [(np.array(a), np.array(b)) for a, b in orig_edges]

    def map_points(self, points):
        """
        :param points: list of points [(x,y), ...]
        :return: list of transformed points
        """
        return [self.map_point(np.array(p)) for p in points]


    def _weight_displ(self, sides):
        displ = np.array([0.0, 0.0])
        wsum = 0.0
        for w, d in sides:
            displ += w * d
            wsum += w
        return displ / wsum

    def map_point(self, p):
        """
        :param p: point as numpy array of size 2
        :return: transformed point
        """
        print("Map p: ", p)
        epsilon = 1e-13
        sides = []
        singular_sides = []
        #ax = plt.gca()
        #ax.margins(0.5)
        for i in range(len(self.edges)):
            X1, X2 = self.edges[i]
            UX1, UX2 = self.displ[i]

            # project to edge
            dX = X2 - X1
            norm = np.array([-dX[1], dX[0]])
            norm = norm / np.linalg.norm(norm)
            dist = np.dot(p - X1, norm)
            # projection of the point to the element
            t_proj = np.linalg.norm(p - X1 - dist * norm) / np.linalg.norm(dX)
            t_proj = max(0.0, t_proj)
            t_proj = min(1.0, t_proj)
            proj_p = X1 + t_proj * dX
            dist = np.linalg.norm( proj_p - p)
            print(t_proj, proj_p, dist)

            dU = UX2 - UX1
            Up = UX1 + t_proj * dU

            #ax.quiver(proj_p[0], proj_p[1], Up[0], Up[1], angles='xy', scale_units='xy', scale=1, color='b')
            #ax.quiver(X1[0], X1[1], UX1[0], UX1[1], angles='xy', scale_units='xy', scale=1, color='g')
            #ax.quiver(X2[0], X2[1], UX2[0], UX2[1], angles='xy', scale_units='xy', scale=1, color='g')

            print(t_proj, proj_p, dist, Up)
            if (dist < epsilon):
                singular_sides.append((1.0, Up))
            else:
                sides.append((1.0 / dist /dist, Up))

        if singular_sides:
            displ = self._weight_displ(singular_sides)
        else:
            displ = self._weight_displ(sides)
        print(displ)
        return p + displ
