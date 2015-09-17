"""
Contains all ModelEditor notifications and their codes.
"""

__author__ = 'Tomas Krizek'


NOTIFICATIONS = {

    # =====================================================
    #                        ERRORS
    # =====================================================

    300: {
        'name': 'Error',
        'description': 'Generic Error',
        'message': 'Unknown Error',
        'example': '',
    },

    # -----------------------------------------------------
    #                  Validation Errors
    # -----------------------------------------------------

    301: {
        'name': 'ValidationError',
        'description': 'Occurs during data validation. More specific error should be used when '
                       'possible.',
        'message': 'Validation Error',
        'example': ''
    },
    302: {
        'name': 'ValidationTypeError',
        'description': 'Validation expects a different type and autoconversion can not resolve the '
                       'correct type.',
        'message': 'Expected type {0}',
        'example': '',
    },
    303: {
        'name': 'ValueTooSmall',
        'description': 'Value is smaller than specified minimum.',
        'message': 'Value has to be larger or equal to {0}',
        'example': '',
    },
    304: {
        'name': 'ValueTooBig',
        'description': 'Value is larger than specified maximum',
        'message': 'Value has to be smaller or equal to {0}',
        'example': '',
    },
    305: {
        'name': 'InvalidOption',
        'description': 'When validating Selection, the given option does not exist.',
        'message': '{0} has not option {1}',
        'example': '',
    },
    306: {
        'name': 'NotEnoughItems',
        'description': 'Array is smaller than its specified minimum size.',
        'message': 'Array has to have at least {0} item(s)',
        'example': '',
    },
    307: {
        'name': 'TooManyItems',
        'description': 'Array is larger than its specified maximum size.',
        'message': 'Array cannot have more than {0} items(s)',
        'example': '',
    },
    308: {
        'name': 'MissingObligatoryKey',
        'description': 'Record is missing an obligatory key.',
        'message': 'Missing obligatory key "{0}" in record {1}',
        'example': '',
    },
    309: {
        'name': 'MissingAbstractRecordType',
        'description': 'AbstractRecord type is missing and has no default_descendant.',
        'message': 'Missing record type',
        'example': '',
    },
    310: {
        'name': 'InvalidAbstractRecordType',
        'description': 'AbstractRecord type is invalid.',
        'message': 'Invalid TYPE "{0}" for record {1}',
        'example': '',
    },



    # =====================================================
    #                        WARNINGS
    # =====================================================

    600: {
        'name': 'Warning',
        'description': 'Generic Warning',
        'message': 'Unknown Warning',
        'example': '',
    },

    # -----------------------------------------------------
    #                  Validation Warnings
    # -----------------------------------------------------


    601: {
        'name': 'ValidationWarning',
        'description': 'Occurs during data validation. More specific warning should be used when '
                       'possible.',
        'message': 'Validation Warning',
        'example': ''
    },
    602: {
        'name': 'UnknownKey',
        'description': 'Unspecified key is encountered in Record.',
        'message': 'Unknown key "{0}" in record {1}',
        'example': '',
    },
}
