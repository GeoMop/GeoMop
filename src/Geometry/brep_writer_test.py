import brep_writer as bw

v1=bw.Vertex((0.0, 0.0, 0.0))
v2=bw.Vertex((0.0, 1.0, 0.0))
v3=bw.Vertex((1.0, 0.0, 0.0))

v4=bw.Vertex((0.0, 0.0, 1.0))
v5=bw.Vertex((0.0, 1.0, 1.0))
v6=bw.Vertex((1.0, 0.0, 1.0))

e1=bw.Edge([v1,v2]) # automatic orientation of edges
e2=bw.Edge([v2,v3])
e3=bw.Edge([v3,v1])

e4=bw.Edge([v4,v5])
e5=bw.Edge([v5,v6])
e6=bw.Edge([v6,v4])

e7=bw.Edge([v1,v4])
e8=bw.Edge([v2,v5])
e9=bw.Edge([v3,v6])

f1=bw.Face([e1, e8, e4.m(), e7.m() ])
f2=bw.Face([e2, e9, e5.m(), e8.m() ])
f3=bw.Face([e3, e7, e6.m(), e4.m() ])
f4=bw.Face([e1,e2,e3])
f5=bw.Face([e4,e5,e6])

shell = bw.Shell([f1,f2,f3,f4,f5])
s1=bw.Solid([ shell ])

c1=bw.Compound([s1])

with open("test_prism.brep", "w") as f:
    bw.write_model(f, c1, bw.Location())