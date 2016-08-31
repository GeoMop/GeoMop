from .data_types_tree import *
import xml.etree.ElementTree as ET


class MeshType(BaseDTT):
    """
    MeshType
    """
    name = "Mesh"
    """Display name of variable type"""
    description = "Type for handling meshes"
    """Display description of variable type"""

    def __init__(self, mesh=None):
        self.__mesh = mesh
        """value"""

    def duplicate(self):
        """
        make deep copy
        """
        return MeshType(mesh=self.__mesh)

    def _to_string(self):
        """Presentation of type in json yaml"""
        return "{\nmesh:" + self.__mesh + "}\n"

    def _get_settings_script(self):
        """return python script, that create instance of this class"""
        if self.__mesh is None:
            return ["MeshType()"]
        return ["MeshType(", "    mesh='{0}'".format(self.__mesh), ")"]

    def _is_set(self):
        """
        return if structure contain real data
        """
        return self.__mesh is not None

    def _assigne(self,  value):
        """
        Assigne appropriate python variable to data
        """
        if isinstance(value, BaseDTT):
            self.__mesh = str(value.value)
        else:
            self.__mesh = str(value)

    def _getter(self):
        """
        Return appropriate python variable to data
        """
        return self.__mesh


class SimulationTime(Float):
    """
    SimulationTime
    """
    name = "SimulationTime"
    """Display name of variable type"""
    description = "Simulation Time"
    """Display description of variable type"""

    def __init__(self, float=None):
        super().__init__(float)

    def duplicate(self):
        """
        make deep copy
        """
        return SimulationTime(self.__float)

    def _get_settings_script(self):
        """return python script, that create instance of this class"""
        if self.__float is None:
            return ["SimulationTime()"]
        return ["SimulationTime({0})".format(str(self.__float))]


class Enum(String):
    """
    Enum
    """

    def __init__(self, option_list, string=None):
        super().__init__(string)
        self.option_list = option_list

    def duplicate(self):
        """
        make deep copy
        """
        return Enum(self.option_list, self.__string)

    def _get_settings_script(self):
        """return python script, that create instance of this class"""
        if self.__string is None:
            return ["Enum()"]
        return ["String('{0}')".format(self.__string)]
        # ToDo: correct functionality

    def _assigne(self, value):
        """
        Assigne appropriate python variable to data
        """
        if isinstance(value, BaseDTT):
            self.__string = str(value.value)
        else:
            self.__string = str(value)


# class RegionEnum(String):
#     def __init__(self, string=None):
#         super().__init__(string)
#
#
# class QuantityEnum(String):
#     def __init__(self, string=None):
#         super().__init__(string)


class PVD_Type():
    # @staticmethod
    # def create_test_data():
    #     return Struct(time=Float(1.0),
    #                   group=String("test"),
    #                   part=Int(1),
    #                   vtk_data=String("data"))

    @staticmethod
    def create_type():
        return Sequence(Struct(time=Float(),
                               group=String(),
                               part=Int(),
                               vtk_data=String()))


    @staticmethod
    def parse_data_from_file(file):
        err = []
        ret = PVD_Type.create_type()
        try:
            tree = ET.parse(file)
            root = tree.getroot()
            for data_set in root.findall("./Collection/DataSet"):
                ret.add_item(Struct(time=Float(float(data_set.attrib["timestep"])),
                                    group=String(data_set.attrib["group"]),
                                    part=Int(int(data_set.attrib["part"])),
                                    vtk_data=String(data_set.attrib["file"])))
        except (ET.ParseError) as e:
            err.append("Parse Error: {0}".format(e))
            #return err
        return ret


class BalanceType():
    @staticmethod
    def create_iner_test_data(region_options, quantity_options):
        return Struct(time=SimulationTime(1.0),
                      region=Enum(region_options, region_options[0]),
                      quantity=Enum(quantity_options, quantity_options[0]),
                      flux=Float(1.0),
                      flux_in=Float(1.0),
                      flux_out=Float(1.0),
                      mass=Float(1.0),
                      source=Float(1.0),
                      source_in=Float(1.0),
                      source_out=Float(1.0),
                      flux_increment=Float(1.0),
                      source_increment=Float(1.0),
                      flux_cumulative=Float(1.0),
                      source_cumulative=Float(1.0),
                      error=Float(1.0))

    @staticmethod
    def create_iner_type(region_options, quantity_options):
        return Struct(time=SimulationTime(),
                      region=Enum(region_options),
                      quantity=Enum(quantity_options),
                      flux=Float(),
                      flux_in=Float(),
                      flux_out=Float(),
                      mass=Float(),
                      source=Float(),
                      source_in=Float(),
                      source_out=Float(),
                      flux_increment=Float(),
                      source_increment=Float(),
                      flux_cumulative=Float(),
                      source_cumulative=Float(),
                      error=Float())

    @staticmethod
    def create_test_data(region_options, quantity_options):
        return Sequence(Tuple(Float(), BalanceType.create_iner_type(region_options, quantity_options)),
                        Tuple(Float(1.0), BalanceType.create_iner_test_data(region_options, quantity_options)),
                        Tuple(Float(2.0), BalanceType.create_iner_test_data(region_options, quantity_options)))

    @staticmethod
    def create_type(region_options, quantity_options):
        return Sequence(Tuple(Float(), BalanceType.create_iner_type(region_options, quantity_options)))


    @staticmethod
    def parse_data_from_file(file, region_options, quantity_options):
        err = []
        ret = BalanceType.create_type(region_options, quantity_options)
        try:
            with open(file, 'r') as fd:
                fd.readline()
                for line in fd:
                    if line[-1] == "\n":
                        line = line[:-1]
                    s = line.split("\t")
                    if len(s) < 15:
                        continue
                    for i in range(len(s)):
                        if s[i][0] == '"' and s[i][-1] == '"':
                            s[i] = s[i][1:-1]
                    time = float(s[0])
                    iner_data = Struct(time=SimulationTime(time),
                                       region=Enum(region_options, s[1]),
                                       quantity=Enum(quantity_options, s[2]),
                                       flux=Float(float(s[3])),
                                       flux_in=Float(float(s[4])),
                                       flux_out=Float(float(s[5])),
                                       mass=Float(float(s[6])),
                                       source=Float(float(s[7])),
                                       source_in=Float(float(s[8])),
                                       source_out=Float(float(s[9])),
                                       flux_increment=Float(float(s[10])),
                                       source_increment=Float(float(s[11])),
                                       flux_cumulative=Float(float(s[12])),
                                       source_cumulative=Float(float(s[13])),
                                       error=Float(float(s[14])))
                    ret.add_item(Tuple(Float(time), iner_data))
        except (RuntimeError, IOError) as e:
            err.append("Can't open balance file: {0}".format(e))
            #return err
        return ret


class PositionVector():
    @staticmethod
    def create_data():
        return Tuple(Float(1.0), Float(1.0), Float(1.0))

    @staticmethod
    def create_type():
        return Tuple(Float(), Float(), Float())


class ObservedQuantitiesType():
    @staticmethod
    def create_data():
        return Struct(a=Float(1.0), b=Float(1.0))

    @staticmethod
    def create_type():
        return Struct(a=Float(), b=Float())


class ObservationType():
    @staticmethod
    def create_iner_data():
        return Struct(time=SimulationTime(1.0),
                      point=PositionVector.create_data(),
                      observation=ObservedQuantitiesType.create_data())

    @staticmethod
    def create_iner_type():
        return Struct(time=SimulationTime(),
                      point=PositionVector.create_type(),
                      observation=ObservedQuantitiesType.create_type())

    @staticmethod
    def create_data():
        return Sequence(Tuple(Float(), ObservationType.create_iner_type()),
                        Tuple(Float(1.0), BalanceType.create_iner_data()),
                        Tuple(Float(2.0), BalanceType.create_iner_data()))


    @staticmethod
    def create_type():
        return Sequence(Tuple(Float(), ObservationType.create_iner_type()))


class XYZEquationResultType():
    @staticmethod
    def create_data():
        return Struct(fields=PVD_Type().create_data,
                      balance=BalanceType.create_data(),
                      observation=ObservationType.create_data())

    @staticmethod
    def create_type():
        return Struct(fields=PVD_Type().create_type,
                      balance=BalanceType.create_type(),
                      observation=ObservationType.create_type())


class FlowOutputType():
    @staticmethod
    def create_data():
        return Struct(mesh=MeshType(mesh="test"),
                      flow_result=XYZEquationResultType.create_data(),
                      solute_result=XYZEquationResultType.create_data(),
                      heat_result=XYZEquationResultType.create_data())

    @staticmethod
    def create_type():
        return Struct(mesh=MeshType(mesh="test"),
                      flow_result=XYZEquationResultType.create_type(),
                      solute_result=XYZEquationResultType.create_type(),
                      heat_result=XYZEquationResultType.create_type())
