import geometry_files.bspline_io as bspline_io
import bspline as bs
import numpy as np

def test_bspline_io():
    def function(x):
        return np.sin(x[0] * 4) * np.cos(x[1] * 4)

    quad = np.array([[1., 3.5], [1., 2.], [2., 2.2], [2, 3.7]])
    poles = bs.make_function_grid(function, 4, 5)
    u_basis = bs.SplineBasis.make_equidistant(2, 2)
    v_basis = bs.SplineBasis.make_equidistant(2, 3)
    surface_func = bs.Surface((u_basis, v_basis), poles[:, :, [2]])
    surface = bs.Z_Surface(quad, surface_func)

    surf_io = bspline_io.bs_zsurface_write(surface)
    surf_new = bspline_io.bs_zsurface_read(surf_io)

    assert np.allclose( surface.center(), surf_new.center())