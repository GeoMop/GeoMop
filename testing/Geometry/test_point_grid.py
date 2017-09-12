import pytest
import point_grid as pg
import math
import numpy as np

def function(x):
    return math.sin(x[0])*math.cos(x[1])

@pytest.fixture
def surface():
    surf = pg.make_function_grid(function, 5, 6)
    return surf

def check_surface(surf, xy_mat, xy_shift, z_shift):
    nu, nv = 30, 40
    # surface on unit square
    U = np.linspace(0.0, 1.0, nu)
    V = np.linspace(0.0, 1.0, nv)
    U_grid, V_grid = np.meshgrid(U,V)

    UV = np.vstack([U_grid.ravel(), V_grid.ravel()])
    XY = xy_mat.dot(UV).T + xy_shift
    Z_grid = surf.eval_in_xy(XY.T)
    eps=0.0
    hx = 1.0 / surf.shape[0]
    hy = 1.0 / surf.shape[1]
    tol = 0.5* ( hx*hx + 2*hx*hy + hy*hy)
    for xy, z_approx in zip(UV.T, Z_grid):
        z_func = function(xy) + z_shift
        eps = max(eps, math.fabs( z_approx - z_func))
        assert math.fabs( z_approx - z_func) < tol
    print("Max norm: ", eps, "Tol: ", tol)

def test_grid_surface(surface):
    xy_mat = np.array([ [1.0, 0.0], [0.0, 1.0] ])
    xy_shift = np.array([0.0, 0.0 ])
    z_shift = 0.0

    check_surface(surface, xy_mat, xy_shift, z_shift)

    # transformed surface
    xy_mat = np.array([ [3.0, -3.0], [2.0, 2.0] ]) / math.sqrt(2)
    xy_shift = np.array([[-2.0, 5.0 ]])
    z_shift = 1.3
    surface.transform(np.concatenate((xy_mat, xy_shift.T), axis=1), z_shift)

    check_surface(surface, xy_mat, xy_shift, z_shift)


