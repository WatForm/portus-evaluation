import argparse
import sys
import testrunner as tr

from eval_portus import result_fields, ignore_fields, result_values, timeout_values

import util


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Runs every specified method on a single file."
    )

    ALLOY_JAR_DEFAULT = '../portus/org.alloytools.alloy.dist/target/org.alloytools.alloy.dist.jar'
    PORTUS_JAR_DEFAULT = 'ca.uwaterloo.watform.portus.cli.PortusCLI'

    parser.add_argument('file', help="The top-level .als file to run on")
    
    scope_group = parser.add_mutually_exclusive_group(required=True)
    scope_group.add_argument('--scope', '-S', type=int, help='scope to run the file at')
    scope_group.add_argument('--default-scopes', action='store_true', help='Use the scopes provided in the file, unaltered')
    
    parser.add_argument('-t', '--timeout',
                        type=int, default=60*60,
                        help="Timeout for each model in seconds")
    parser.add_argument('--command', type=int, default=1, help="Command number to run in the file 1-indexed")

    methods_group = parser.add_mutually_exclusive_group(required=False)
    methods_group.add_argument('-m', '--methods',
                        nargs='+', type=str,
                        choices=util.PORTUS_METHODS.keys(),
                        default=['portus', 'kodkod', 'unoptimized'],
                        help='What methods to run')
    methods_group.add_argument('--all-methods', help='use all methods',
                            action='store_true')

    parser.add_argument('--alloy-jar',
                        default=ALLOY_JAR_DEFAULT,
                        help='Path to the alloy jar'
                        )
    parser.add_argument('--iterations', type=int, default=1,
                        help="Times to run each test")
    output_group = parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument('-o', '--output',
                    type=argparse.FileType('w'),
                    help='The file to write the csv file out to.')
    output_group.add_argument('--use-stdout', help='Write to stdout instead of a csv file', action='store_true')

    args = parser.parse_args()

    if args.all_methods:
        args.methods = util.PORTUS_METHODS.keys()
        
    # Set output file to stdout
    if args.use_stdout:
        args.output = sys.stdout

    command = ''
    if args.default_scopes:
        command = f'java -Xmx30g -Xms30g -cp {args.alloy_jar} ca.uwaterloo.watform.portus.cli.PortusCLI {{method_args}} -command {args.command} {args.file}'
    else:
        command = f'java -Xmx30g -Xms30g -cp {args.alloy_jar} ca.uwaterloo.watform.portus.cli.PortusCLI {{method_args}} -all-scopes {args.scope} -command {args.command} {args.file}'

    # Get the methods to run through
    methods_used = {key: util.PORTUS_METHODS[key] for key in args.methods}
    method_options = [{'method': method, 'method_args': method_args}
                    for (method, method_args) in methods_used.items()]
    method_opt = tr.Option('method_opt', method_options)
    
    runner = tr.CSVTestRunner(command,
                           method_opt,
                           timeout=args.timeout,
                           output_file=args.output,
                           result_fields=result_fields,
                           fields_from_result=result_values,
                           fields_from_timeout=timeout_values,
                           ignore_fields=ignore_fields,
                           )
    
    runner.run(args.iterations, force_skip_header=True)
