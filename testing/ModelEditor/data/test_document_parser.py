import data.yaml.document_parser as dp
from data.error_handler import ErrorHandler


def test_remove_diff_block():
    document_parser = dp.DocumentParser(ErrorHandler())
    document_parser.current_doc = '\n'.join([
        "a:",
        "  - 0",
        "  - 1",
        "  - 2",
        "b:",
        "  - b0",
        "  - b2",
        "c:& 3",
        "d: 5",
        "e: 5"
    ])
    document_parser.parsed_doc = '\n'.join([
        "a:",
        "  - 0",
        "  - 1",
        "b:",
        "  - b0",
        "  - b1",
        "  - b2",
        "c: 3",
        "d: 4",
        "e: 5"
    ])
    document_parser._error_line = 7
    diffed_doc = document_parser._remove_diff_blocks()
    assert diffed_doc[3] == '#  - 2\n'
    assert diffed_doc[7] == '#c:& 3\n'
    assert diffed_doc[8] == '#d: 5\n'


def test_parser():
    error_handler = ErrorHandler()
    document_parser = dp.DocumentParser(error_handler)
    document = '\n'.join([
        "problem: ",
        "  primary_equation:",
        "    balance: true"
    ])
    root_node = document_parser.parse(document)
    assert (root_node.get_child('problem').get_child('primary_equation')
            .get_child('balance')).value is True

    # first edit - start typing
    document = '\n'.join([
        "output",
        "problem: ",
        "  primary_equation:",
        "    balance: true"
    ])
    error_handler.clear()
    root_node = document_parser.parse(document)
    assert (root_node.get_child('problem').get_child('primary_equation')
            .get_child('balance')).value is True
    assert len(error_handler.errors) == 2

    # second edit - correct
    document = '\n'.join([
        "output: test",
        "problem: ",
        "  primary_equation:",
        "    balance: true"
    ])
    error_handler.clear()
    root_node = document_parser.parse(document)
    assert root_node.get_child('output').value == 'test'

    # third edit - modify
    document = '\n'.join([
        "output:test",
        "problem: ",
        "  primary_equation:",
        "    balance: true"
    ])
    error_handler.clear()
    root_node = document_parser.parse(document)
    assert (root_node.get_child('problem').get_child('primary_equation')
            .get_child('balance')).value is True
    assert len(error_handler.errors) == 2

    # fourth edit - another error
    document = '\n'.join([
        "output:test",
        "problem: ",
        "  primary_equation:",
        "    input_fie",
        "    balance: true"
    ])
    error_handler.clear()
    root_node = document_parser.parse(document)
    assert len(error_handler.errors) == 3


if __name__ == '__main__':
    test_parser()
