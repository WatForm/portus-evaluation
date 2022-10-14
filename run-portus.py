#!/usr/bin/env python

"""
Run Portus on many files and output SMTLIB++.
"""

import argparse
import os
import os.path
import shutil


DEFAULT_ALLOY_JAR_LOCATION = (
    '../org.alloytools.alloy/org.alloytools.alloy.dist/'
    'target/org.alloytools.alloy.dist.jar'
)
DEFAULT_FORTRESS_JAR_DIR = '../org.alloytools.alloy/org.alloytools.fortress.core/libs'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run Alloy files through Portus and dump them to SMTLIB++.')
    parser.add_argument('--alloy-jar', '-j', default=DEFAULT_ALLOY_JAR_LOCATION, help='Path to the Alloy dist jar')
    parser.add_argument('--fortress-jar-dir', '-f', default=DEFAULT_FORTRESS_JAR_DIR,
        help='Path to the directory containing the Fortress jar and dependencies')
    parser.add_argument('alloyfiles', nargs='+', help='Alloy files to run through Portus')
    return parser.parse_args()


def dump_file(alloy_jar_path: str, fortress_dir_path: str, alloy_filename: str):
    # Run it through Portus manually
    result = os.system(
        "java -cp '{alloy_jar}{dir_sep}{fortress_dir}/*' -DfortressDumpToSmtlib=yes "
        'edu.mit.csail.sdg.alloy4whole.SimpleCLI {alloy_filename}'.format(
            alloy_jar=alloy_jar_path,
            dir_sep=os.pathsep, # Windows uses a different separator
            fortress_dir=fortress_dir_path,
            alloy_filename=alloy_filename))
    if result != 0:
        raise RuntimeError('Alloy invocation returned {}'.format(result))
    
    # The above command output to a temporary file whose name is in .alloy.tmp
    with open('.alloy.tmp', 'r') as output_file:
        output = output_file.readlines()

    # Delete the unwanted .alloy.tmp file
    os.remove('.alloy.tmp')

    # There should be one line that looks like "Output to: {filename}"
    prefix = 'Output to: '
    try:
        smtlib_filename = next(line.strip()[len(prefix):] for line in output if line.startswith(prefix))
    except StopIteration:
        raise RuntimeError('No SMTLIB output filename found')

    # Copy it to the Alloy file's directory
    alloy_dirname = os.path.dirname(alloy_filename)
    desired_smtlib_basename = os.path.basename(alloy_filename)
    if desired_smtlib_basename.endswith('.als'):
        desired_smtlib_basename = desired_smtlib_basename[:-len('.als')]
    desired_smtlib_basename += '.smtlib'
    smtlib_location = alloy_dirname + '/' + desired_smtlib_basename
    shutil.copy(smtlib_filename, smtlib_location)
    print('Dumped to', smtlib_location)


def main():
    args = parse_args()
    for alloy_filename in args.alloyfiles:
        print('Running {} through Portus...'.format(alloy_filename))
        try:
            dump_file(args.alloy_jar, args.fortress_jar_dir, alloy_filename)
        except Exception as e:
            print('Error:', e)


if __name__ == '__main__':
    main()
