"""
usage:
    importer.py [-h]
    [--transformation-name [TRANSFORMATION_NAME [TRANSFORMATION_NAME ...]]]
    [--destination-file [DESTINATION_FILE]] --con_file CON_FILE

Parameters::

    -h, --help
        show this help message and exit
    --transformation-name [TRANSFORMATION_NAME [TRANSFORMATION_NAME ...]]
        Transformation rules contained in the Model Editor that are processed after import
    --destination-file [DESTINATION_FILE]
        The destination file if is different from source file
    --con_file CON_FILE
        Con input file

Description:
    Importer translate Flow123d con file to yaml format. TYPE parameters is
    transformed to tags (!value). Importer try rewrite references to yaml
    format and place it to appropriate place. Comments are copied and
    place to yaml file.  If is set some transformation rules, they are processed
    after import in set order by :mod:`data.yaml.transformator`.
"""

import os
import sys

import argparse

from ModelEditor.meconfig import MEConfig as cfg


if __name__ == "__main__":
    def main():
        """Launches the import cli."""
        parser = argparse.ArgumentParser(
            description='Import the YAML configuration file from CON format')
        parser.add_argument('--transformation-name', nargs='*',
                            help='Transformation rules contained in the Model Editor that are '
                                 'processed after import')
        parser.add_argument('--destination-file', nargs='?', default=None,
                            help='The destination file if is different from source file')
        parser.add_argument('--con_file', help='CON input file', required=True)
        args = parser.parse_args()

        if args.destination_file:
            file = args.destination_file
        else:
            file = os.path.splitext(args.con_file)[0] + '.yaml'  # replace extension
        if os.path.isfile(file):
            raise Exception("File already exists")

        cfg.init(None)
        cfg.set_current_format_file("1.8.3")
        cfg.import_file(args.con_file)
        if args.transformation_name is not None:
            for transf in args.transformation_name:
                cfg.transform_con(transf)

        file_d = open(file, 'w')
        file_d.write(cfg.document)
        file_d.close()

    main()
