import numpy as np
import numpy.linalg as la

class InvalidGridExc(Exception):
    pass


class GridSurface:
    """
    Surface given as bilinear interpolation of a regular grid of points.
    TODO: This can be viewed as a degree 1 Z-function B-spline. Make it a common class for any degree??
    """
    step_tolerance = 1e-10

    def __init__(self):
        """
        Initialize point grid from numpy array.
        :param grid: NxMx3 numpy array of NxM grid of #D coordinates
        """
        self.grid=None
        self.mat_xy_to_uv=None
        self.mat_uv_to_xy=None
        self.shift=None
        self.shape = (0,0)
        self.uv_step = (0,0)


    def load(self, filename):
        """
        Load the grid surface from file
        :param filename:
        :return:
        """
        point_seq = np.loadtxt(filename)
        assert min(point_seq.shape) > 1
        self.init_from_seq(point_seq.T)


    def init_from_seq(self, point_seq):
        """
        Get 2d transform matrix 2 rows 3 cols to map a grid of XY points to unit square
        :param point_seq: numpy array N x 2
        :return:
        """

        assert point_seq.shape[0] == 3
        n_points = point_seq.shape[1]
        point_seq_xy = point_seq[0:2,:]
        u_step = point_seq_xy[0:2,1] - point_seq_xy[0:2, 0]
        for i in range(2, n_points):
            step = point_seq_xy[:,i] - point_seq_xy[:,i-1]
            if la.norm(u_step - step) > self.step_tolerance:
                break

        v_step = point_seq_xy[:,i] - point_seq_xy[:,0]

        nu = i
        nv = int(n_points / nu)
        if not n_points == nu*nv:
            raise InvalidGridExc("Not a M*N grid.")

        # check total range of the grid
        u_range_0 = point_seq_xy[:, nu-1] - point_seq_xy[:, 0]
        u_range_1 = point_seq_xy[:, -1] - point_seq_xy[:, -nu]
        v_range_0 = point_seq_xy[:, -nu] - point_seq_xy[:, 0]
        v_range_1 = point_seq_xy[:, -1] - point_seq_xy[:, nu-1]
        if not la.norm(u_range_0 - u_range_1) < self.step_tolerance or \
            not la.norm(v_range_0 - v_range_1) < self.step_tolerance:
            raise InvalidGridExc("Grid XY envelope is not a parallelogram.")

        u_step = u_range_0 / (nu-1)
        v_step = v_range_0 / (nv-1)

        # check regularity of the grid
        for i in range(nu*nv):
            pred_x = i - 1
            pred_y = i - nu
            if i%nu == 0:
                pred_x= -1
            if pred_x > 0 and not la.norm(point_seq_xy[:, i] - point_seq_xy[:, pred_x] - u_step) < 2*self.step_tolerance:
                raise InvalidGridExc("Irregular grid in X direction, point %d"%i)
            if pred_y > 0 and not la.norm(point_seq_xy[:, i] - point_seq_xy[:, pred_y] - v_step) < 2*self.step_tolerance:
                raise InvalidGridExc("Irregular grid in Y direction, point %d"%i)

        self.shape = (nu, nv)
        self.uv_step = ( 1.0 / float(nu-1), 1.0 / float(nv-1) )
        self.xy_shift = point_seq_xy[:, 0]
        self.z_scale = 1.0
        self.z_shift = 0.0
        self.mat_uv_to_xy = np.column_stack((u_range_0, v_range_0))
        self.mat_xy_to_uv = la.inv(self.mat_uv_to_xy)

        self.grid = point_seq[2,:].reshape(nv, nu)

    def transform(self, xy_mat, z_mat):
        """
        Transform the surface by arbitrary XY linear transform and Z shift.
        :param xy_mat: np array, 2 rows 3 cols, last column is xy shift
        :param z_shift: float
        :return: None
        """
        assert xy_mat.shape == (2, 3)
        assert z_mat.shape == (2, )
        self.mat_uv_to_xy = xy_mat[0:2,0:2].dot( self.mat_uv_to_xy )
        self.xy_shift = xy_mat[0:2,0:2].dot( self.xy_shift ) + xy_mat[0:2, 2]
        self.mat_xy_to_uv = la.inv(self.mat_uv_to_xy)

        self.z_scale *= z_mat[0]
        self.z_shift = z_mat[0] * self.z_shift + z_mat[1]

    def get_xy_envelope(self):
        return self.uv_to_xy(np.array([[0,0], [1,0], [1,1], [0,1]]).T)




    def xy_to_uv(self, xy_points):
        """
        :param xy_points: numpy matrix 2 rows N cols
        :return: matrix of UV coordinates
        """
        assert xy_points.shape[0] == 2
        return self.mat_xy_to_uv.dot((xy_points.T - self.xy_shift).T)


    def uv_to_xy(self, uv_points):
        """
        :param xy_points: numpy matrix 2 rows N cols
        :return: matrix of UV coordinates
        """
        assert uv_points.shape[0] == 2, "Size: {}".format(uv_points.shape)
        return (self.mat_uv_to_xy.dot(uv_points).T + self.xy_shift).T


    def eval_in_xy(self, points):
        """
        Return np array of z-values.
        :param points: np array N x 2 of XY cooridinates
        :return:
        """

        assert points.shape[0] == 2, "Size: {}".format(points.shape)
        uv_points = self.xy_to_uv(points)
        return self.eval_in_uv(uv_points)


    def eval_in_uv(self, uv_points):
        """
        Return np array of z-values.
        :param points: np array N x 2 of XY cooridinates
        :return:
        """

        assert uv_points.shape[0] == 2

        result = np.zeros(uv_points.shape[1])
        for i, uv in enumerate(uv_points.T):
            iuv = np.floor(uv / self.uv_step)
            iu = max(0, min(self.shape[0] - 2, int(iuv[0])))
            iv = max(0, min(self.shape[1] - 2, int(iuv[1])))
            iuv = np.array([iu, iv])

            uv_loc = uv / self.uv_step - iuv
            u_loc = np.array([1 - uv_loc[0], uv_loc[0]])
            v_loc = np.array([1 - uv_loc[1], uv_loc[1]])
            Z_mat = self.grid[iv: (iv + 2), iu: (iu + 2)]
            result[i] = self.z_scale*(v_loc.dot(Z_mat).dot(u_loc)) + self.z_shift
        return result

    def plot_matplot_lib(self, fig_ax, nu=None, nv=None, **kwargs):
        """

        :param fig_ax: Matplotlib figure axes
        :param nu: Num of plot points in U direction.
        :param nv: Num of plot points in V direction.
        :return:
        """
        if nu == None:
            nu = self.shape[0]
        if nv == None:
            nv = self.shape[1]

        # Make data.
        U = np.linspace(0.0, 1.0, nu)
        V = np.linspace(0.0, 1.0, nv)
        U,V = np.meshgrid(U,V)
        points = np.vstack( [U.ravel(), V.ravel()] )

        XY = self.uv_to_xy( points )
        Z = self.eval_in_uv( points )

        X, Y = XY[0], XY[1]
        X = X.reshape(U.shape)
        Y = Y.reshape(U.shape)
        Z = Z.reshape(U.shape)

        # Plot the surface.
        surf = fig_ax.plot_surface(X, Y,  Z, **kwargs)

        return surf





def make_function_grid(func, nu, nv):

    U = np.linspace(0, 1.0, nu)
    V = np.linspace(0, 1.0, nv)
    U,V = np.meshgrid(U,V)
    points_uv = np.stack([U.ravel(), V.ravel()], 1)
    Z = np.apply_along_axis(func, 1, points_uv)
    points = np.stack([U.ravel(), V.ravel(), Z], 1)
    surf = GridSurface()
    surf.init_from_seq(points.T)
    return surf








# TODO: visualize the surface evaluated using eval_xy
if __name__ == "__main__":
    """
    Visual test.
    """

    def plot_surface(surf):
        '''
        ======================
        3D surface (color map)
        ======================

        Demonstrates plotting a 3D surface colored with the coolwarm color map.
        The surface is made opaque by using antialiased=False.

        Also demonstrates using the LinearLocator and custom formatting for the
        z axis tick labels.
        '''

        from mpl_toolkits.mplot3d import Axes3D
        import matplotlib.pyplot as plt
        from matplotlib import cm
        from matplotlib.ticker import LinearLocator, FormatStrFormatter
        import numpy as np


        fig = plt.figure()
        ax = fig.gca(projection='3d')

        surf_plot = surf.plot_matplot_lib(ax, 50, 30, cmap=cm.coolwarm,
                               linewidth=0, antialiased=False)

        # Customize the z axis.
        #ax.set_zlim(-1.01, 1.01)
        #ax.zaxis.set_major_locator(LinearLocator(10))
        #ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

        # Add a color bar which maps values to colors.
        #fig.colorbar(surf_plot, shrink=0.5, aspect=5)

        plt.show()


    #import math
    #surf=make_function_grid(lambda x: math.sin(x[0])*(math.cos(x[1])), 5, 4)

    surf = GridSurface()
    surf.load("test_data/test_surface_Hradek_200x200.csv")

    plot_surface(surf)
