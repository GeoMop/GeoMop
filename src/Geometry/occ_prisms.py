from OCC.Display.SimpleGui import init_display
import OCC
import OCC.gp
import OCC.BRepLib

display, start_display, add_menu, add_function_to_menu = init_display()

min_z = 0
max_z = 1


def extrude_point(point_pair):
    pt,pb = point_pair
    point_top = OCC.gp.gp_Pnt(pt[0], pt[1], max_z)
    point_bot = OCC.gp.gp_Pnt(pb[0], pb[1], min_z)
    edge = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeEdge(point_top, point_bot)
    return (point_top, point_bot, edge)

def v_edges_from_points(points_top, points_bot):
    return [ extrude_point(p) for p in zip(points_top, points_bot) ]

def v_faces_from_edges(v_edges, lines):
    faces = []
    for line in lines:
        p0_t,p0_b, e0 = v_edges[line[0]]
        p1_t,p1_b, e1 = v_edges[line[1]]

        e_t = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeEdge(p0_t, p1_t)
        e_b = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeEdge(p0_b, p1_b)

        # Vertical face
        wire = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeWire()
        wire.Add(e0.Edge())
        wire.Add(e_t.Edge())
        wire.Add(e1.Edge())
        wire.Add(e_b.Edge())
        face = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeFace(wire.Wire())

        faces.append([ e_t, e_b, face ])

    return faces

def solids_from_poly(v_faces, poly):
    solids = []
    for pol in poly:

        sewing = OCC.BRepBuilderAPI.BRepBuilderAPI_Sewing(0.01, True, True, True, False)
        sewing.SetFloatingEdgesMode(True)

        top_wire = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeWire()
        bot_wire = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeWire()

        for idx_face in pol:
            i_face=abs(idx_face)
            #assert(i_face != 0)
            negative = (idx_face < 0)
            e_t, e_b, face = v_faces[i_face]
            face_shape = face.Shape()
            et_shape = e_t.Edge()
            eb_shape = e_b.Edge()
            if negative:
                face_shape.Orientation(OCC.TopAbs.TopAbs_REVERSED)
                et_shape.Orientation(OCC.TopAbs.TopAbs_REVERSED)
                eb_shape.Orientation(OCC.TopAbs.TopAbs_REVERSED)
            sewing.Add(face_shape)

            # extend cup wires
            top_wire.Add(et_shape)
            bot_wire.Add(eb_shape)

        top_face = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeFace(top_wire.Wire())
        sewing.Add(top_face.Shape())
        bot_face = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeFace(bot_wire.Wire())
        sewing.Add(bot_face.Shape())

        # Sew it all together
        sewing.Perform()
        sewing_shape = sewing.SewedShape()
        # Create shell, solid and compound
        shell = OCC.TopoDS.topods_Shell(sewing_shape)
        make_solid = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeSolid()
        make_solid.Add(shell)
        solid = make_solid.Solid()

        #builder = OCC.BRep.BRep_Builder()
        #builder.MakeSolid(solid)
        #builder.Add(solid, shell)

        # Try to fix orientation of solid volume
        #OCC.BRepLib.breplib().OrientClosedSolid(solid)

        solids.append(solid)

    return solids

################################################33333

def internal_fracture():

    points_top=[
        [0,0],      # 0
        [1, 0],     # 1
        [0,1],      # 2
        [0.5,0.5]]      # 3
    lines=[
        [0,1],      # 0
        [1,2],      # 1
        [2,0],      # 2
        [2,3]]      # 6

    poly=[[0,1,3,-3,2]]

    return [points_top, points_top, lines, poly]


def two_prisms():
    points_top = [
        [0, 0],  # 0
        [1, 0],  # 1
        [2, 1],  # 2
        [1, 2],  # 3
        [0, 1]]  # 4

    points_bot = [
        [0, 0],  # 0
        [1, 0],  # 1
        [2, 1],  # 2
        [1, 2],  # 3
        [0, 1]]  # 4

    lines = [
        [0, 1],  # 0
        [1, 2],  # 1
        [2, 3],  # 2
        [3, 4],  # 3
        [4, 0],  # 4
        [1, 4]]  # 5

    poly = [[0, 5, 4], [1, 2, 3, -5]]

    return [points_top, points_bot, lines, poly]


#data = internal_fracture()
data=two_prisms()
points_top, points_bot, lines, poly = data
#poly=[ [0, 5, 4] ]
#poly=[ [1,2,3, -5]]


points_top=[ [0.0, 0.0], [0.0, 1.0], [1.0, 0.0]]
lines = [ [0,1], [1,2], [2,0] ]
poly = [[0,1,2]]

v_edges=v_edges_from_points(points_top, points_top)

#v_edges=v_edges_from_points(points_top, points_bot)
v_faces=v_faces_from_edges(v_edges, lines)
solids=solids_from_poly(v_faces, poly)

#solid = create_prism(prism_points)

builder = OCC.BRep.BRep_Builder()
comp = OCC.TopoDS.TopoDS_Compound()
builder.MakeCompound(comp)
for solid in solids:
    builder.Add(comp, solid);


OCC.BRepTools.breptools_Write(comp, "prism_output.brep")

display.DisplayShape(comp, update=True)
start_display()
