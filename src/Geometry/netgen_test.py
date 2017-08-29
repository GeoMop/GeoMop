import os

import netgen
print(netgen.__file__)
import netgen.meshing as ngmesh
import netgen.csg as ngcsg
import netgen.NgOCC as ngocc

file="breps/3_prism_full.brep"
mesh_file=os.path.splitext(file)[0] + ".mesh.ng"
geom=ngocc.LoadOCC_BREP("breps/3_prism_full.brep")
geom


param = ngmesh.MeshingParameters()
param.maxh = 10
print (param)

mesh = ngocc.GenerateMesh(geom, param)
#m1.SecondOrder()

#import exportNeutral
#exportNeutral.Export (m1, "shaft.mesh")



mesh.Save(mesh_file)
mesh.Export("breps/export.msh","Gmsh2 Format")