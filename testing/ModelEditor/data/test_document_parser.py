import data.yaml.document_parser as dp
from data.error_handler import ErrorHandler


def test_parser():
    error_handler = ErrorHandler()
    document_parser = dp.DocumentParser(error_handler)
    document = '\n'.join([
        "problem: ",
        "  primary_equation:",
        "    balance: true",
        "    - 2"
    ])
    root_node = document_parser.parse(document)
    assert (root_node.get_child('problem').get_child('primary_equation')
            .get_child('balance')).value is True
    assert len(error_handler.errors) == 1


if __name__ == '__main__':
    test_parser()
