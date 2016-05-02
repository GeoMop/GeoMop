import os

input_files = \
"""
transform_test_data/01_flow_bddc.con
transform_test_data/01_flow_gmsh.con
transform_test_data/01_flow_vtk.con
transform_test_data/01_flow_vtk_nobalance.con
transform_test_data/01_flow_vtk_piezo.con
transform_test_data/02_flow_gmsh.con
transform_test_data/02_flow_implicit_fields_gmsh.con
transform_test_data/02_flow_implicit_old.con
transform_test_data/02_flow_vtk.con
transform_test_data/03_flow_implicit.con
transform_test_data/03_flow_implicit_nobalance.con
transform_test_data/03_flow_vtk.con
transform_test_data/03_flow_vtk_nobalance.con
transform_test_data/03_output_input_fields.con
transform_test_data/05_flow_dirichlet.con
transform_test_data/05_flow_neumann.con
transform_test_data/05_flow_robin.con
transform_test_data/06_flow_21d.con
transform_test_data/06_flow_32d.con
transform_test_data/06_1D2D.con
transform_test_data/06_2D2D.con
transform_test_data/08_flow_vtk.con
transform_test_data/09_flow_time_dep.con
transform_test_data/10_flow_LMH.con
transform_test_data/10_flow_LMH_nobalance.con
transform_test_data/10_flow_MH.con
transform_test_data/10_flow_MH_nobalance.con
transform_test_data/11_flow_decay_long_gmsh.con
transform_test_data/12_decay_time_seqence.con
transform_test_data/12_decay_vtk.con
transform_test_data/12_flow_decay_molar_mass_vtk.con
transform_test_data/12_lin_react_vtk.con
transform_test_data/13_flow_gmsh.con
transform_test_data/13_flow_implicit.con
transform_test_data/14_short_pulse_explicit.con
transform_test_data/14_short_pulse_implicit.con
transform_test_data/14_trans_explicit.con
transform_test_data/14_trans_implicit.con
transform_test_data/15_flow_trans_explicit.con
transform_test_data/15_flow_trans_implicit.con
transform_test_data/16_flow.con
transform_test_data/16_flow_implicit.con
transform_test_data/16_flow_implicit_time_dep.con
transform_test_data/16_flow_small.con
transform_test_data/17_flow_decay_vtk.con
transform_test_data/18_flow_implicit.con
transform_test_data/18_flow_implicit_elementwise.con
transform_test_data/19_flow_large_cube_gmsh.con
transform_test_data/19_flow_large_cube_vtk.con
transform_test_data/19_flow_small_cube.con
transform_test_data/20_flow_vtk_simple.con
transform_test_data/20_flow_vtk_source.con
transform_test_data/20_freundlich_new.con
transform_test_data/20_freundlich_var.con
transform_test_data/20_langmuir_new.con
transform_test_data/20_langmuir_var.con
transform_test_data/20_linear_new.con
transform_test_data/20_linear_var.con
transform_test_data/20_linear_var_jump.con
transform_test_data/20_test_20.con
transform_test_data/20_test_20_sorp_rock.con
transform_test_data/21_flow_heat.con
transform_test_data/22_compatible.con
transform_test_data/22_noncompatible_P0.con
transform_test_data/22_noncompatible_P1.con
transform_test_data/23_dual_por_cfl.con
transform_test_data/23_dual_por.con
transform_test_data/23_dual_por_linear.con
transform_test_data/23_dual_por_pade.con
transform_test_data/23_dual_por_sorp.con
transform_test_data/23_dual_por_sorp_linear.con
transform_test_data/23_dual_por_time.con
transform_test_data/24_diffusive_flux_implicit.con
transform_test_data/24_dirichlet_implicit.con
transform_test_data/24_inflow_explicit.con
transform_test_data/24_inflow_implicit.con
transform_test_data/24_total_flux_implicit.con
""".splitlines(False)

output_files = \
"""
transform_test_data/01_flow_bddc.yaml
transform_test_data/01_flow_gmsh.yaml
transform_test_data/01_flow_vtk.yaml
transform_test_data/01_flow_vtk_nobalance.yaml
transform_test_data/01_flow_vtk_piezo.yaml
transform_test_data/02_flow_gmsh.yaml
transform_test_data/02_flow_implicit_fields_gmsh.yaml
transform_test_data/02_flow_implicit_old.yaml
transform_test_data/02_flow_vtk.yaml
transform_test_data/03_flow_implicit.yaml
transform_test_data/03_flow_implicit_nobalance.yaml
transform_test_data/03_flow_vtk.yaml
transform_test_data/03_flow_vtk_nobalance.yaml
transform_test_data/03_output_input_fields.yaml
transform_test_data/05_flow_dirichlet.yaml
transform_test_data/05_flow_neumann.yaml
transform_test_data/05_flow_robin.yaml
transform_test_data/06_flow_21d.yaml
transform_test_data/06_flow_32d.yaml
transform_test_data/06_1D2D.yaml
transform_test_data/06_2D2D.yaml
transform_test_data/08_flow_vtk.yaml
transform_test_data/09_flow_time_dep.yaml
transform_test_data/10_flow_LMH.yaml
transform_test_data/10_flow_LMH_nobalance.yaml
transform_test_data/10_flow_MH.yaml
transform_test_data/10_flow_MH_nobalance.yaml
transform_test_data/11_flow_decay_long_gmsh.yaml
transform_test_data/12_decay_time_seqence.yaml
transform_test_data/12_decay_vtk.yaml
transform_test_data/12_flow_decay_molar_mass_vtk.yaml
transform_test_data/12_lin_react_vtk.yaml
transform_test_data/13_flow_gmsh.yaml
transform_test_data/13_flow_implicit.yaml
transform_test_data/14_short_pulse_explicit.yaml
transform_test_data/14_short_pulse_implicit.yaml
transform_test_data/14_trans_explicit.yaml
transform_test_data/14_trans_implicit.yaml
transform_test_data/15_flow_trans_explicit.yaml
transform_test_data/15_flow_trans_implicit.yaml
transform_test_data/16_flow.yaml
transform_test_data/16_flow_implicit.yaml
transform_test_data/16_flow_implicit_time_dep.yaml
transform_test_data/16_flow_small.yaml
transform_test_data/17_flow_decay_vtk.yaml
transform_test_data/18_flow_implicit.yaml
transform_test_data/18_flow_implicit_elementwise.yaml
transform_test_data/19_flow_large_cube_gmsh.yaml
transform_test_data/19_flow_large_cube_vtk.yaml
transform_test_data/19_flow_small_cube.yaml
transform_test_data/20_flow_vtk_simple.yaml
transform_test_data/20_flow_vtk_source.yaml
transform_test_data/20_freundlich_new.yaml
transform_test_data/20_freundlich_var.yaml
transform_test_data/20_langmuir_new.yaml
transform_test_data/20_langmuir_var.yaml
transform_test_data/20_linear_new.yaml
transform_test_data/20_linear_var.yaml
transform_test_data/20_linear_var_jump.yaml
transform_test_data/20_test_20.yaml
transform_test_data/20_test_20_sorp_rock.yaml
transform_test_data/21_flow_heat.yaml
transform_test_data/22_compatible.yaml
transform_test_data/22_noncompatible_P0.yaml
transform_test_data/22_noncompatible_P1.yaml
transform_test_data/23_dual_por_cfl.yaml
transform_test_data/23_dual_por.yaml
transform_test_data/23_dual_por_linear.yaml
transform_test_data/23_dual_por_pade.yaml
transform_test_data/23_dual_por_sorp.yaml
transform_test_data/23_dual_por_sorp_linear.yaml
transform_test_data/23_dual_por_time.yaml
transform_test_data/24_diffusive_flux_implicit.yaml
transform_test_data/24_dirichlet_implicit.yaml
transform_test_data/24_inflow_explicit.yaml
transform_test_data/24_inflow_implicit.yaml
transform_test_data/24_total_flux_implicit.yaml
""".splitlines(False)

from meconfig import cfg

def test_transf():
    path = os.path.dirname(os.path.realpath(__file__))

    global input_files, output_files
    for i in range(0, len(input_files)):
        if input_files[i]=="":
            continue
        input = os.path.join(path, input_files[i])
        output = output_files[i]
        print(input)
        
        cfg.init(None)
        cfg.import_file(input)
        cfg.transform("flow123d")
        
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
