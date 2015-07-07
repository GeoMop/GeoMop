from data.meconfig import MEConfig as cfg
from data.meconfig import _Config as Config
from data.yaml import Loader

def set_empty_config():
    Config.SERIAL_FILE = "ModelEditorData_test"
    cfg.init(None)
    cfg.config = Config()
    
def clean_config():
    import config
    config.delete_config_file("ModelEditorData_test")
 
def load_complex_structure_to_config():
    document = (
        "output_streams:\n"
        "- file: \n"
        "  format: flow_output_stream\n"
        "- file: dual_por_transport.pvd\n"
        "  time_step: 0.5\n"
        "\n"
        "problem:\n"
        "  description: Some, text\n"
        "  primary_equation:\n"
        "    balance: true\n"
        "    input_fields:\n"
        "    - {conductivity: 1.0e-15, r_set: ALL}\n"
        "    - {bc_pressure: 0, bc_type: dirichlet, r_set: BOUNDARY}\n"
    )
    loader = Loader()
    cfg.root = loader.load(document) 
