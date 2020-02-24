import os

input_files = \
"""
transform_test_data/01_flow_bddc.con
transform_test_data/02_flow_gmsh.con
transform_test_data/03_flow_implicit.con
transform_test_data/05_flow_dirichlet.con
transform_test_data/06_flow_21d.con
""".splitlines(False)

output_files = \
"""
transform_test_data/01_flow_bddc.yaml
transform_test_data/02_flow_gmsh.yaml
transform_test_data/03_flow_implicit.yaml
transform_test_data/05_flow_dirichlet.yaml
transform_test_data/06_flow_21d.yaml
""".splitlines(False)

from ModelEditor.meconfig import MEConfig as cfg

def test_transf():
    path = os.path.dirname(os.path.realpath(__file__))

    global input_files, output_files
    for i in range(0, len(input_files)):
        if input_files[i]=="":
            continue
        input = os.path.join(path, input_files[i])
        output = os.path.join(path, output_files[i])
        print(input)
        
        cfg.init(None)
        cfg.import_file(input)
        cfg.transform("2.0.0_rc")
        
        with open(output) as f:
            templ = f.readlines()
        doc = cfg.document.splitlines(False)
            
        assert len(templ) == len(doc), \
            "Len of template {0} and result {1} is diferent {1}!={2}.".format(
            output, input,  len(templ),  len(doc))
        for i in range(0, len(doc)):
            assert templ[i].rstrip() == doc[i].rstrip(), \
                "Difference in line {0}\n(template {1}, result {2})\n{3}\n<>\n{4}".format(
                str(i+1), output,  input, templ[i].rstrip(), doc[i].rstrip())
