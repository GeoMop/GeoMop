import os

__sample_dir__ = os.path.join(os.path.split(os.path.split(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0])[0])[0], "sample","ModelEditor", "TransformFiles" )

def load_empty_tranformation_file():
    with open(os.path.join(__sample_dir__, 'empty.json')) as file:
        document = file.read()
        return document
    return None
