import subprocess
import os

import testrunner as tr
import util

import argparse
from typing import *


ALLOY_JAR_DEFAULT = '../portus/org.alloytools.alloy.dist/target/org.alloytools.alloy.dist.jar'
PORTUS_JAR_DEFAULT = 'ca.uwaterloo.watform.portus.cli.PortusCLI'

result_fields = ['return_code', 'time_elapsed']
ignore_fields = ['method_args']

# Fill in result fields when the process completes
def result_values(opts: tr.OptionDict, result: subprocess.CompletedProcess, time_elapsed: float) -> tr.OptionDict:
    results = {
        'return_code': result.returncode,
        'time_elapsed': time_elapsed
    }
    return results


# Fill in result fields when the process times out
def timeout_values(opts: tr.OptionDict, result: subprocess.TimeoutExpired) -> tr.OptionDict:
    results = {
        'return_code': 999,
        'time_elapsed': -1
    }
    return results


models = tr.FromFileOption('model', 'expert-models-list.txt')

methods = {
    'portus': '-r',
    'kodkod': '-rk',
    'unoptimized': '-r -disable-all-opts -b',  # Include -b to increase bitwidth as required
}
method_names = list(methods.keys())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='portus tests',
        description='An evaluation script for Portus'
    )
    
    parser.add_argument('-t', '--timeout',
                        type=int, default=60*60,
                        help='Timeout for each model in seconds')
    parser.add_argument('-o', '--output',
                    type=argparse.FileType('w'),
                    default=f'test-{util.now_string()}.csv',
                    help='The file to write the csv file out to.')
    parser.add_argument('-v', '--verbose',
                        action='store_true')
    parser.add_argument('-m', '--methods',
                        nargs='+', type=str,
                        choices=method_names,
                        default=method_names,
                        help='What methods to run',
                        )
    parser.add_argument('--alloy-jar',
                        default=ALLOY_JAR_DEFAULT,
                        help='Path to the alloy jar'
                        )
    parser.add_argument('--portus-jar',
                        default=PORTUS_JAR_DEFAULT,
                        help=f'Module to the portus jar ({PORTUS_JAR_DEFAULT})'
                        )
    
    rerun_group = parser.add_argument_group('re-run adjustments')
    
    rerun_group.add_argument('-i', '--iterations',
                        type=int, default=1,
                        help='The number of iterations to run each set of arguments')
    rerun_group.add_argument('-s', '--skip',
                        type=int, default=0,
                        help='Number of values to skip')
    rerun_group.add_argument('--force-header', action='store_true',
                        help='forces the header to be written to the output file')
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f'{parser=}')
    
    # command = f'java -cp {args.alloy_jar} {args.portus_jar} {{method_args}} {{model}}'
    command = f'java -cp {args.alloy_jar} {args.portus_jar} {{method_args}} -command 1 {{model}}'
    # Generate options for methods chosen
    # Create the lined options 'method' and 'method_args'
    methods_used = {key: methods[key] for key in args.methods}
    method_options = [{'method': method, 'method_args': method_args} for (method, method_args) in methods_used.items()]
    
    method_opt = tr.Option('method_opt',method_options)
    
    runner = tr.CSVTestRunner(command,
        models, method_opt, 
        timeout=args.timeout,
        output_file=args.output,
        result_fields=result_fields,
        fields_from_result=result_values,
        fields_from_timeout=timeout_values,
        ignore_fields=ignore_fields,
    )
    
    if args.verbose:
        util.setup_logging_debug()
    else:
        util.setup_logging_default()
    
    runner.run(args.iterations, args.skip)
