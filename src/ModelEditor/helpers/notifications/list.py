"""
Contains all ModelEditor notifications and their codes.
"""

__author__ = 'Tomas Krizek'


_NOTIFICATIONS = [

    # =====================================================
    #                  FATAL ERRORS
    # =====================================================

    {
        'code': 100,
        'name': 'FatalError',
        'description': 'Generic Fatal Error',
        'message': '{0}',
        'example': '',
    },

    # -----------------------------------------------------
    #                Syntax Fatal Errors
    # -----------------------------------------------------

    {
        'code': 101,
        'name': 'SyntaxFatalError',
        'description': 'Occurs when pyyaml can not parse the input.',
        'message': 'Unable to parse remaining input',
        'example': ''
    },

    # =====================================================
    #                        ERRORS
    # =====================================================

    {
        'code': 300,
        'name': 'Error',
        'description': 'Generic Error',
        'message': '{0}',
        'example': '',
    },

    # -----------------------------------------------------
    #                  Validation Errors
    # -----------------------------------------------------

    {
        'code': 301,
        'name': 'ValidationError',
        'description': 'Occurs during data validation. More specific error should be used when '
                       'possible.',
        'message': '{0}',
        'example': ''
    },
    {
        'code': 302,
        'name': 'ValidationTypeError',
        'description': 'Validation expects a different type and autoconversion can not resolve the '
                       'correct type.',
        'message': 'Expected type {0}',
        'example': '',
    },
    {
        'code': 303,
        'name': 'ValueTooSmall',
        'description': 'Value is smaller than specified minimum.',
        'message': 'Value has to be larger or equal to {0}',
        'example': '',
    },
    {
        'code': 304,
        'name': 'ValueTooBig',
        'description': 'Value is larger than specified maximum',
        'message': 'Value has to be smaller or equal to {0}',
        'example': '',
    },
    {
        'code': 305,
        'name': 'InvalidSelectionOption',
        'description': 'When validating Selection, the given option does not exist.',
        'message': '{0} has not option {1}',
        'example': '',
    },
    {
        'code': 306,
        'name': 'NotEnoughItems',
        'description': 'Array is smaller than its specified minimum size.',
        'message': 'Array has to have at least {0} item(s)',
        'example': '',
    },
    {
        'code': 307,
        'name': 'TooManyItems',
        'description': 'Array is larger than its specified maximum size.',
        'message': 'Array cannot have more than {0} items(s)',
        'example': '',
    },
    {
        'code': 308,
        'name': 'MissingObligatoryKey',
        'description': 'Record is missing an obligatory key.',
        'message': 'Missing obligatory key "{0}" in record {1}',
        'example': '',
    },
    {
        'code': 309,
        'name': 'MissingAbstractRecordType',
        'description': 'AbstractRecord type is missing and has no default_descendant.',
        'message': 'Missing record type',
        'example': '',
    },
    {
        'code': 310,
        'name': 'InvalidAbstractRecordType',
        'description': 'AbstractRecord type is invalid.',
        'message': 'Invalid TYPE "{0}" for record {1}',
        'example': '',
    },

    # -----------------------------------------------------
    #                  Format Errors
    # -----------------------------------------------------

    {
        'code': 400,
        'name': 'FormatError',
        'description': 'Occurs when format file is invalid. More specific warning should be used '
                       'when possible.',
        'message': '{0}',
        'example': ''
    },
    {
        'code': 401,
        'name': 'InputTypeNotSupported',
        'description': 'Format contains an input type that is not supported.',
        'message': 'Unexpected input_type "{0}" in format',
        'example': '',
    },

    # -----------------------------------------------------
    #                  Syntax Errors
    # -----------------------------------------------------

    {
        'code': 500,
        'name': 'SyntaxError',
        'description': 'Occurs when YAML syntax is invalid. More specific error should be used '
                       'when possible.',
        'message': '{0}',
        'example': ''
    },
    {
        'code': 501,
        'name': 'UndefinedAnchor',
        'description': 'The anchor is not yet defined.',
        'message': 'Anchor "&{0}" is not defined',
        'example': '',
    },
    {
        'code': 502,
        'name': 'ComplexMappingKey',
        'description': 'When user attempts to use an array or record as a key.',
        'message': 'Only scalar keys are supported for records',
        'example': ''
    },
    {
        'code': 503,
        'name': 'InvalidMergeNode',
        # TODO: less confusing description, message
        'description': 'When non-alias node should be merged.',
        'message': 'Only alias or an array of aliases can be merged',
        'example': ''
    },
    {
        'code': 504,
        # TODO: test and figure out name
        'name': 'InvalidAnchorTypeForMerge',
        'description': 'When user attempts to merge an anchor node that is not a Record.',
        'message': 'Anchor node "&{0}" is not a Record',
        'example': ''
    },
    {
        'code': 505,
        'name': 'ConstructScalarError',
        'description': 'Scalar value can not be constructed from the input.',
        'message': '{0}',
        'example': ''
    },


    # =====================================================
    #                        WARNINGS
    # =====================================================

    {
        'code': 600,
        'name': 'Warning',
        'description': 'Generic Warning',
        'message': '{0}',
        'example': '',
    },

    # -----------------------------------------------------
    #                  Validation Warnings
    # -----------------------------------------------------

    {
        'code': 601,
        'name': 'ValidationWarning',
        'description': 'Occurs during data validation. More specific warning should be used when '
                       'possible.',
        'message': '{0}',
        'example': ''
    },
    {
        'code': 602,
        'name': 'UnknownRecordKey',
        'description': 'Unspecified key is encountered in Record.',
        'message': 'Unknown key "{0}" in record {1}',
        'example': '',
    },

    # =====================================================
    #                   INFO MESSAGES
    # =====================================================

    {
        'code': 800,
        'name': 'Info',
        'description': 'Generic Info',
        'message': '{0}',
        'example': '',
    },

    # -----------------------------------------------------
    #                  Validation Info
    # -----------------------------------------------------

    {
        'code': 801,
        'name': 'ValidationInfo',
        'description': 'Occurs during data validation. More specific info should be used when '
                       'possible.',
        'message': '{0}',
        'example': ''
    },

    # -----------------------------------------------------
    #                  Syntax Info
    # -----------------------------------------------------

    {
        'code': 900,
        'name': 'SyntaxInfo',
        'description': 'Occurs during syntax parsing. More specific info should be used when '
                       'possible.',
        'message': '{0}',
        'example': ''
    },
    {
        'code': 901,
        'name': 'UselessTag',
        'description': 'When tag is found anywhere except AbstractRecord.',
        'message': 'Tag "!{0}" has no effect here',
        'example': ''
    },
    {
        'code': 902,
        'name': 'OverridingAnchor',
        'description': 'When an anchor with the same name was defined previously.',
        'message': 'Previously defined anchor "&{0}" overwritten',
        'example': ''
    },
]


NOTIFICATIONS_BY_CODE = {notification['code']: notification for notification in _NOTIFICATIONS}
NOTIFICATIONS_BY_NAME = {notification['name']: notification for notification in _NOTIFICATIONS}
