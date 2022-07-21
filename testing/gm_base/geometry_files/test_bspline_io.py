import gm_base.geometry_files.bspline_io as bspline_io
import bgem.bspline.bspline as bs
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
    xy_map = [[0.1, 0.2, -2], [0.2, - 0.1, -1]]
    z_map = [2.0, 5.0]
    surface.transform(xy_map, z_map )

    surf_io = bspline_io.bs_zsurface_write(surface)
    surf_new = bspline_io.bs_zsurface_read(surf_io)

    assert np.allclose(xy_map, surf_new.get_transform()[0])
    assert np.allclose(z_map, surf_new.get_transform()[1])
    assert np.allclose( surface.center(), surf_new.center())

    surface.transform(xy_map)
    assert np.allclose(surface.center(), surf_new.center())

    xy_map = [[0.2, 0.3, -3], [0.3, - 0.2, -2]]
    z_map = [3, 6]
    surface.transform(xy_map)
    surf_new.transform(xy_map)
    assert np.allclose(surface.center(), surf_new.center())

