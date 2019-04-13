import numpy as np
import matplotlib.pyplot as plt
import scipy
import math
import random

# TODO:
# - Try deformation of square.


def cross2d(a, b):
    return a[0]*b[1] - a[1]*b[0]



def rotate(lst):
    return lst[-1:] + lst[:-1]



class BEMMapping:
    """
    Class to compute deformation of a polygon (possibly nonconvex).
    Polygon and its deformation is given as a  list of inital positions of vertices (orig_points),
    and a  list of displaced vertices (new_points). The points must be ordered anto-clockwise aroud the polygon.
    """
    def __init__(self, orig_points, new_points, lamme):
        assert( len(orig_points) == len(new_points))
        self.n_nodes=len(orig_points)
        lam, mu = lamme
        UC0=(lam+mu)/(4*math.pi*mu)/(lam+2*mu)
        UC1=(lam+3*mu)/(lam+mu)
        TC2=(lam-mu)/(2*math.pi)/(lam+2*mu)
        TC3=mu/(lam+mu)
        self.params=(UC0,UC1,TC2,TC3)
        self.mu=mu
        self.lam=lam

        self.displ=np.array(new_points)-np.array(orig_points)
        self.nodes= [ np.array(p) for p in orig_points]
        self.compute_tractions()
        self.setup_qpoints()

    def plot_def_and_tractions(self):
        ax = plt.gca()
        X,Y = zip(*self.nodes)
        #U,V = zip(*self.displ)
        #ax.quiver(X, Y, U, V, angles='xy', scale_units='xy', scale=1, color='g')

        L, R, N1, N2 = zip(*self.trac)
        U,V = zip(*L)
        ax.quiver(X, Y, U, V, angles='xy', scale_units='xy', scale=1, color='r')
        U, V = zip(*R)
        ax.quiver(X, Y, U, V, angles='xy', scale_units='xy', scale=1, color='r')
        #U,V = zip(*N1)
        #ax.quiver(X, Y, U, V, angles='xy', scale_units='xy', scale=1, color='b')
        #U,V = zip(*N2)
        #ax.quiver(X, Y, U, V, angles='xy', scale_units='xy', scale=1, color='b')

        # PLOT Q points
        #(X, w, T, U, N) = zip(*self.qpoints)
        #X, Y = zip(*X)
        #ax.plot(X, Y, 'o', color='m')
        #U, V = zip(*N)
        #ax.quiver(X, Y, U, V, angles='xy', scale_units='xy', scale=1, color='m')



    def compute_tractions(self):
        self.trac=[0.0] * self.n_nodes
        for i in range(len(self.nodes)):
            """
            (st) parametrization near B point
            X=B+s(B-A)+t(C-B)
            """
            A = self.nodes[i - 2]
            B = self.nodes[i - 1]
            C = self.nodes[i]
            # AB side is parametrized by s, BC parametrized by t
            dX_by_ds = B - A
            dX_by_dt = C - B
            xy_by_st = np.array( [ dX_by_ds, dX_by_dt ])

            dA = self.displ[i-2]
            dB = self.displ[i - 1]
            dC = self.displ[i]
            # gradient of displacement in s,t coordinates
            grad_st_displ = np.array([ dB-dA, dC-dB]).T
            # transform to gradient in x,y coordinates, used to compute strain tensor
            grad_xy_displ = grad_st_displ.dot(xy_by_st)
            #print("Points:", A, B, C)
            #print(xy_by_st)
            #print(grad_st_displ)
            #print(grad_xy_displ)
            tension = self.mu*(grad_xy_displ + grad_xy_displ.T) + self.lam*np.eye(2)*np.trace(grad_xy_displ)
            #print(tension)
            norm_AB = np.array( [dX_by_ds[1], -dX_by_ds[0]] )
            norm_AB = norm_AB / np.linalg.norm(norm_AB)
            norm_BC = np.array( [dX_by_dt[1], -dX_by_dt[0]] )
            norm_BC = norm_BC / np.linalg.norm(norm_BC)
            self.trac[i-1] = ( tension.dot(norm_AB), tension.dot(norm_BC), norm_BC, norm_AB) # left and right limit

    def setup_qpoints(self):
        self.qpoints=[]
        gauss_deg=32
        points, weights = np.polynomial.legendre.leggauss(gauss_deg)
        print(sum(weights)/2.0)
        gauss = list(zip(points, weights))
        for i in range(len(self.nodes)):
            # element nodes
            X1 = self.nodes[i-1]
            X2 = self.nodes[i]
            dX = X2 - X1
            TX1 = self.trac[i - 1][1]
            TX2 = self.trac[i][0]
            dT = TX2 - TX1
            N = self.trac[i-1][2] # normal
            UX1 = self.displ[i - 1]
            UX2 = self.displ[i]
            dU = UX2 - UX1
            for (point, weight) in gauss:
                t = (point + 1.0) * 0.5
                X = X1 + t*dX
                w = weight * np.linalg.norm(dX) * 0.5
                T = TX1 + t*dT
                U = UX1 + t*dU
                self.qpoints.append( (X, w, T, U, N) )





    '''
    def assembly(self):
        """
        Assembly Tu (displacement to trastion) and Ut (traction to displacement) matrices.
        :return:
        """
        self.UT=np.zeros((2*self.n_nodes, 2*self.n_nodes))
        self.TU=self.UT
        for i_row in range(self.n_nodes):
            for i_col in range(self.n_nodes):
                Uxx=Uyy=Uxy=Txx=Tyy=Txy=Tyx=0.0

                for () in qpoints:
                    Uxx +=
                    Uyy +=
                    Uxy +=
                    Txx +=
                    Tyy +=
                    Txy +=
                    Tyx +=
    '''



    def map_points(self,points):
        return [ self.map_point(np.array(p)) for p in points ]

    def fundamental_ut(self, P, Q, N):
        (UC0, UC1, TC2, TC3)=self.params
        R = Q - P
        Rx_sqr = R[0] * R[0]
        Ry_sqr = R[1] * R[1]
        r_sqr = Rx_sqr + Ry_sqr
        r = math.sqrt(r_sqr)
        inv_r = 1.0 / r
        log_inv_r = -math.log(r)
        Rxy_norm = R[0] * R[1] / r_sqr

        Uxx = UC0 * (UC1 * log_inv_r + Rx_sqr / r_sqr)
        Uyy = UC0 * (UC1 * log_inv_r + Ry_sqr / r_sqr)
        Uxy = UC0 * Rxy_norm

        cos_pq = R.dot(N) / r
        sin_pq = cross2d(R,N) / r
        Txx = -TC2 * (TC3 + 2 * Rx_sqr / r_sqr) * cos_pq / r
        Tyy = -TC2 * (TC3 + 2 * Ry_sqr / r_sqr) * cos_pq / r
        Txy = - TC2 / r * ( 2 * Rxy_norm * cos_pq - TC3 * sin_pq )
        Tyx = - TC2 / r * ( 2 * Rxy_norm * cos_pq + TC3 * sin_pq )

        U = np.array([ [Uxx, Uxy], [Uxy, Uyy] ])
        T = np.array([ [Txx, Txy], [Tyx, Tyy] ])
        return (U, T)


    def map_point_bem(self, p):
        assert(len(p)==2)
        displacement=np.array([0.0, 0.0])
        for (Q, w, T, U, N) in self.qpoints:
            (fU,fT)=self.fundamental_ut(p, Q, N)
            #T=[0,0]
            displacement += (fU.dot(T) + fT.dot(U)) * w
        return p + displacement

    def weight_displ(self, sides):
        displ=np.array([0.0, 0.0])
        wsum = 0.0
        for w, d in sides:
            displ += w * d
            print("w: ", w, )
            wsum += w
        return displ / wsum

    def map_point(self, p):
        epsilon = 1e-13
        sides = []
        singular_sides = []
        sum_dist=0.0
        for i in range(len(self.nodes)):
            X1 = self.nodes[i-1]
            X2 = self.nodes[i]

            # signed distance of the point
            dX = X2 - X1
            norm = np.array([-dX[1], dX[0]])
            norm = norm / np.linalg.norm(norm)
            dist = np.dot(p - X1, norm)
            # projection of the point to the element
            t_proj = np.linalg.norm(p - X1 - dist * norm) / np.linalg.norm(dX)
            UX1 = self.displ[i - 1]
            UX2 = self.displ[i]
            dU = UX2 - UX1
            Up = UX1 + t_proj * dU

            if (dist < epsilon):
                singular_sides.append( (1.0, Up) )
            else:
                sides.append( (1.0/dist, Up) )

        if singular_sides:
            return p + self.weight_displ(singular_sides)

        return p + self.weight_displ(sides)




