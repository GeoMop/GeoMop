import json
import hashlib


class YamlSupportRemote:
    """
    Class for extract regions, params, active processes
    and mesh file from .yaml files.
    """

    def __init__(self):
        self.regions = []
        self.params = []
        self.active_processes = []
        self.mesh_file = ""
        self.yaml_file_hash = ""
        self.mesh_file_hash = ""

    def get_regions(self):
        """Return regions."""
        return self.regions.copy()

    def get_params(self):
        """Return params."""
        return self.params.copy()

    def get_active_processes(self):
        """Return active processes."""
        return self.active_processes.copy()

    def get_mesh_file(self):
        """Return mesh file."""
        return self.mesh_file

    def get_yaml_file_hash(self):
        """Return yaml file hash."""
        return self.yaml_file_hash

    def get_mesh_file_hash(self):
        """Return mesh file hash."""
        return self.mesh_file_hash

    def save(self, file):
        """Save data to file."""
        err = []
        try:
            with open(file, 'w') as fd:
                d = dict(regions=self.regions,
                         params=self.params,
                         active_processes=self.active_processes,
                         mesh_file=self.mesh_file,
                         yaml_file_hash=self.yaml_file_hash,
                         mesh_file_hash=self.mesh_file_hash)
                json.dump(d, fd, indent=4, sort_keys=True)
        except Exception as e:
            err.append("YamlSupport saving error: {0}".format(e))
        return err

    def load(self, file):
        """Load data form file."""
        err = []
        try:
            with open(file, 'r') as fd:
                d = json.load(fd)

                self.regions = d["regions"] if "regions" in d else []
                self.params = d["params"] if "params" in d else []
                self.active_processes = d["active_processes"] if "active_processes" in d else []
                self.mesh_file = d["mesh_file"] if "mesh_file" in d else ""
                self.yaml_file_hash = d["yaml_file_hash"] if "yaml_file_hash" in d else ""
                self.mesh_file_hash = d["mesh_file_hash"] if "mesh_file_hash" in d else ""
        except Exception as e:
            err.append("YamlSupport loading error: {0}".format(e))
        return err

    @staticmethod
    def file_hash(file):
        """Compute hash from file."""
        err = []
        hash = hashlib.sha512()
        try:
            with open(file, 'r') as file_d:
                for line in file_d:
                    hash.update(bytes(line, "utf-8"))
        except (RuntimeError, IOError) as e:
            err.append("Can't open file: {0}".format(e))
        return err, hash.hexdigest()
