import json
from .geometry_structures import LayerGeometry

class GeometrySer:
    """geometry data serializer"""
    
    def __init__(self, file):
        self.file = file
        """Json geometry file"""
        
    def read(self):
        """return LayerGeometry data"""
        with open(self.file) as f:
            contents = f.read()
        obj = json.loads(contents, encoding="utf-8")
        lg = LayerGeometry(obj)
        return lg
        
        
    def write(self, lg):
        """Write LayerGeometry data to file"""
        with open(self.file, 'w') as f:
            json.dump(lg.serialize(), f, indent=4, sort_keys=True)
        
