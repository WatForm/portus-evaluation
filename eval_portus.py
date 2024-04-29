import subprocess
import os
import logging

import testrunner as tr
import util

import argparse
from typing import *


ALLOY_JAR_DEFAULT = '../portus/org.alloytools.alloy.dist/target/org.alloytools.alloy.dist.jar'

result_fields = ['return_code', 'time_elapsed']
ignore_fields = ['method_args']

# Fill in result fields when the process completes
def result_values(opts: tr.OptionDict, result: subprocess.CompletedProcess, time_elapsed: float) -> tr.OptionDict:
    if result.returncode != 0:
        logging.debug('------OUTPUT------\n' + result.stdout + '------STDERR-----\n' + result.stderr +"------------")
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


# models = tr.FromFileOption('model', 'expert-models-list.txt')
models_and_cmds = tr.CSVOption('models_and_cmds', 'expert-models.csv')



methods = util.PORTUS_METHODS
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
    
    methods_group = parser.add_mutually_exclusive_group(required=False)
    
    methods_group.add_argument('-m', '--methods',
                        nargs='+', type=str,
                        choices=method_names,
                        default=['portus', 'kodkod', 'unoptimized'],
                        help='What methods to run',
                        )
    methods_group.add_argument('--all-methods', help='use all methods', action='store_true')
    
    
    scopes_group = parser.add_mutually_exclusive_group(required=False)
    scopes_group.add_argument('--scopes',
                        nargs='+', type=int,
                        default=[2,4,8,16,32],
                        help='The scopes at which to test'
                        )
    scopes_group.add_argument('--default-scopes', action='store_true', help='Use scopes defined in the files')
    parser.add_argument('--alloy-jar',
                        default=ALLOY_JAR_DEFAULT,
                        help='Path to the alloy jar'
                        )
    parser.add_argument('--corpus-root',
                        default='.',
                        help='Directory containing the expert models')
    
    
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
    
    if args.all_methods:
        args.methods = method_names
    
    if args.verbose:
        print(f'{args=}')
    
    # command = f'java -cp {args.alloy_jar} {args.portus_jar} {{method_args}} {{model}}'
    command = f'java -Xmx30g -Xms30g -cp {args.alloy_jar} ca.uwaterloo.watform.portus.cli.PortusCLI {{method_args}} -all-scopes {{scope}} -command {{command_number}} {args.corpus_root}/{{model}}'
    
    if args.default_scopes:
        command = f'java -Xmx30g -Xms30g -cp {args.alloy_jar} ca.uwaterloo.watform.portus.cli.PortusCLI {{method_args}} -command {{command_number}} {args.corpus_root}/{{model}}'
        args.scopes = [8]  # This should just be a default value so we don't run commands multiple times
    
    # Generate options for methods chosen
    # Create the lined options 'method' and 'method_args'
    methods_used = {key: methods[key] for key in args.methods}
    method_options = [{'method': method, 'method_args': method_args} for (method, method_args) in methods_used.items()]
    
    method_opt = tr.Option('method_opt',method_options)
    
    scope_opt = tr.Option('scope', args.scopes)
    
    
    runner = tr.CSVTestRunner(command,
        scope_opt, models_and_cmds, method_opt, 
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
