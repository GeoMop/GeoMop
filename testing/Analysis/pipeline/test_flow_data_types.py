from geomop_analysis import YamlSupportLocal
from Analysis.pipeline.flow_data_types import *
import pytest

this_source_dir = os.path.dirname(os.path.realpath(__file__))
def data_file(test_path):
    return os.path.join(this_source_dir, "flow_data_types_res", test_path)

def test_flow_data_types():
    # 01 - flow equation
    ys = YamlSupportLocal()
    err = ys.parse(data_file("01/flow_gmsh.yaml"))
    assert len(err) == 0

    type = FlowOutputType.create_type(ys)
    test_type = Struct(
        flow_result=(
            Struct(
                balance=(
                    Sequence(
                        (
                            Tuple(
                                Float(),
                                (
                                    Struct(
                                        error=Float(),
                                        flux=Float(),
                                        flux_cumulative=Float(),
                                        flux_in=Float(),
                                        flux_increment=Float(),
                                        flux_out=Float(),
                                        mass=Float(),
                                        quantity=Enum(['water_volume']),
                                        region=Enum(['.1d_channel', '.2d_fracture_1', '.2d_fracture_2', '.3d_cube',
                                                     '.IMPLICIT_BOUNDARY', '1d_channel', '2d_fracture_1',
                                                     '2d_fracture_2', '3d_cube', 'ALL']),
                                        source=Float(),
                                        source_cumulative=Float(),
                                        source_in=Float(),
                                        source_increment=Float(),
                                        source_out=Float(),
                                        time=SimulationTime()
                                    )
                                )
                            )
                        )
                    )
                )
            )
        ),
        mesh=String()
    )
    assert type._match_type(test_type)
    assert test_type._match_type(type)

    data = FlowOutputType.create_data(ys, data_file("01/output"))
    assert type._match_type(data)
    assert data._match_type(type)
    assert len(data.flow_result.balance._list) == 8
    assert data.flow_result.balance.tail()[0] == 0.0
    assert data.flow_result.balance.tail()[1].flux_out == -0.102171
    assert data.flow_result.balance.tail()[1].quantity == "water_volume"
    assert data.mesh == "./input/test1_new.msh"

    # 02 - solute equation
    ys = YamlSupportLocal()
    err = ys.parse(data_file("02/flow_lin_sorption_dg.yaml"))
    assert len(err) == 0

    type = FlowOutputType.create_type(ys)
    test_type = Struct(
        flow_result=(
            Struct(
                balance=(
                    Sequence(
                        (
                            Tuple(
                                Float(),
                                (
                                    Struct(
                                        error=Float(),
                                        flux=Float(),
                                        flux_cumulative=Float(),
                                        flux_in=Float(),
                                        flux_increment=Float(),
                                        flux_out=Float(),
                                        mass=Float(),
                                        quantity=Enum(['water_volume']),
                                        region=Enum(['.1d', '.2d', '.IMPLICIT_BOUNDARY', '1d', '2d', 'ALL']),
                                        source=Float(),
                                        source_cumulative=Float(),
                                        source_in=Float(),
                                        source_increment=Float(),
                                        source_out=Float(),
                                        time=SimulationTime()
                                    )
                                )
                            )
                        )
                    )
                ),
                fields=(
                    Sequence(
                        (
                            Struct(
                                group=String(),
                                part=Int(),
                                time=Float(),
                                vtk_data=String()
                            )
                        )
                    )
                )
            )
        ),
        mesh=String(),
        solute_result=(
            Struct(
                balance=(
                    Sequence(
                        (
                            Tuple(
                                Float(),
                                (
                                    Struct(
                                        error=Float(),
                                        flux=Float(),
                                        flux_cumulative=Float(),
                                        flux_in=Float(),
                                        flux_increment=Float(),
                                        flux_out=Float(),
                                        mass=Float(),
                                        quantity=Enum(['A', 'B']),
                                        region=Enum(['.1d', '.2d', '.IMPLICIT_BOUNDARY', '1d', '2d', 'ALL']),
                                        source=Float(),
                                        source_cumulative=Float(),
                                        source_in=Float(),
                                        source_increment=Float(),
                                        source_out=Float(),
                                        time=SimulationTime()
                                    )
                                )
                            )
                        )
                    )
                ),
                fields=(
                    Sequence(
                        (
                            Struct(
                                group=String(),
                                part=Int(),
                                time=Float(),
                                vtk_data=String()
                            )
                        )
                    )
                )
            )
        )
    )
    assert type._match_type(test_type)
    assert test_type._match_type(type)

    data = FlowOutputType.create_data(ys, data_file("02/output"))
    assert type._match_type(data)
    assert data._match_type(type)
    assert len(data.solute_result.balance._list) == 132
    assert data.solute_result.balance.tail()[0] == 10.0
    assert data.solute_result.balance.tail()[1].flux_out == -2.00083
    assert data.solute_result.balance.tail()[1].quantity == "B"
    assert len(data.solute_result.fields._list) == 11
    assert data.solute_result.fields.tail().vtk_data == "transport_dg/transport_dg-000010.vtu"


    # 21 - heat equation
    ys = YamlSupportLocal()
    err = ys.parse(data_file("21/flow_heat.yaml"))
    assert len(err) == 0

    type = FlowOutputType.create_type(ys)
    test_type = Struct(
        flow_result=(
            Struct(
                balance=(
                    Sequence(
                        (
                            Tuple(
                                Float(),
                                (
                                    Struct(
                                        error=Float(),
                                        flux=Float(),
                                        flux_cumulative=Float(),
                                        flux_in=Float(),
                                        flux_increment=Float(),
                                        flux_out=Float(),
                                        mass=Float(),
                                        quantity=Enum(['water_volume']),
                                        region=Enum(['.IMPLICIT_BOUNDARY', '.fracture_bottom', '.fracture_top', '.left',
                                                     '.right', '.rock_bottom', '.rock_top', 'ALL', 'fracture', 'rock']),
                                        source=Float(),
                                        source_cumulative=Float(),
                                        source_in=Float(),
                                        source_increment=Float(),
                                        source_out=Float(),
                                        time=SimulationTime()
                                    )
                                )
                            )
                        )
                    )
                ),
                fields=(
                    Sequence(
                        (
                            Struct(
                                group=String(),
                                part=Int(),
                                time=Float(),
                                vtk_data=String()
                            )
                        )
                    )
                )
            )
        ),
        heat_result=(
            Struct(
                balance=(
                    Sequence(
                        (
                            Tuple(
                                Float(),
                                (
                                    Struct(
                                        error=Float(),
                                        flux=Float(),
                                        flux_cumulative=Float(),
                                        flux_in=Float(),
                                        flux_increment=Float(),
                                        flux_out=Float(),
                                        mass=Float(),
                                        quantity=Enum(['energy']),
                                        region=Enum(['.IMPLICIT_BOUNDARY', '.fracture_bottom', '.fracture_top', '.left',
                                                     '.right', '.rock_bottom', '.rock_top', 'ALL', 'fracture', 'rock']),
                                        source=Float(),
                                        source_cumulative=Float(),
                                        source_in=Float(),
                                        source_increment=Float(),
                                        source_out=Float(),
                                        time=SimulationTime()
                                    )
                                )
                            )
                        )
                    )
                ),
                fields=(
                    Sequence(
                        (
                            Struct(
                                group=String(),
                                part=Int(),
                                time=Float(),
                                vtk_data=String()
                            )
                        )
                    )
                )
            )
        ),
        mesh=String()
    )
    assert type._match_type(test_type)
    assert test_type._match_type(type)

    data = FlowOutputType.create_data(ys, data_file("21/output"))
    assert type._match_type(data)
    assert data._match_type(type)
    assert len(data.heat_result.balance._list) == 99
    assert data.heat_result.balance.tail()[0] == 10.0
    assert data.heat_result.balance.tail()[1].flux_out == -32.9754
    assert data.heat_result.balance.tail()[1].quantity == "energy"
    assert len(data.heat_result.fields._list) == 11
    assert data.heat_result.fields.tail().vtk_data == "heat/heat-000010.vtu"

    # 02_2 - balance file name
    ys = YamlSupportLocal()
    err = ys.parse(data_file("02_2/flow_lin_sorption_dg.yaml"))
    assert len(err) == 0

    type = FlowOutputType.create_type(ys)
    test_type = Struct(
        flow_result=(
            Struct(
                balance=(
                    Sequence(
                        (
                            Tuple(
                                Float(),
                                (
                                    Struct(
                                        error=Float(),
                                        flux=Float(),
                                        flux_cumulative=Float(),
                                        flux_in=Float(),
                                        flux_increment=Float(),
                                        flux_out=Float(),
                                        mass=Float(),
                                        quantity=Enum(['water_volume']),
                                        region=Enum(['.1d', '.2d', '.IMPLICIT_BOUNDARY', '1d', '2d', 'ALL']),
                                        source=Float(),
                                        source_cumulative=Float(),
                                        source_in=Float(),
                                        source_increment=Float(),
                                        source_out=Float(),
                                        time=SimulationTime()
                                    )
                                )
                            )
                        )
                    )
                ),
                fields=(
                    Sequence(
                        (
                            Struct(
                                group=String(),
                                part=Int(),
                                time=Float(),
                                vtk_data=String()
                            )
                        )
                    )
                )
            )
        ),
        mesh=String(),
        solute_result=(
            Struct(
                balance=(
                    Sequence(
                        (
                            Tuple(
                                Float(),
                                (
                                    Struct(
                                        error=Float(),
                                        flux=Float(),
                                        flux_cumulative=Float(),
                                        flux_in=Float(),
                                        flux_increment=Float(),
                                        flux_out=Float(),
                                        mass=Float(),
                                        quantity=Enum(['A', 'B']),
                                        region=Enum(['.1d', '.2d', '.IMPLICIT_BOUNDARY', '1d', '2d', 'ALL']),
                                        source=Float(),
                                        source_cumulative=Float(),
                                        source_in=Float(),
                                        source_increment=Float(),
                                        source_out=Float(),
                                        time=SimulationTime()
                                    )
                                )
                            )
                        )
                    )
                ),
                fields=(
                    Sequence(
                        (
                            Struct(
                                group=String(),
                                part=Int(),
                                time=Float(),
                                vtk_data=String()
                            )
                        )
                    )
                )
            )
        )
    )
    assert type._match_type(test_type)
    assert test_type._match_type(type)

    data = FlowOutputType.create_data(ys, data_file("02_2/output"))
    assert type._match_type(data)
    assert data._match_type(type)
    assert len(data.solute_result.balance._list) == 132
    assert data.solute_result.balance.tail()[0] == 10.0
    assert data.solute_result.balance.tail()[1].flux_out == -2.00083
    assert data.solute_result.balance.tail()[1].quantity == "B"
    assert len(data.solute_result.fields._list) == 11
    assert data.solute_result.fields.tail().vtk_data == "transport_dg/transport_dg-000010.vtu"
