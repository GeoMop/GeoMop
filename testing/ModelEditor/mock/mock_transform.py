def load_empty_tranformation_file():
    with open('../../sample/ModelEditor/TransformFiles/empty.json') as file:
        document = file.read()
        return document
    return None
