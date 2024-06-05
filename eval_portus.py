#!venv/bin/python3

"""
    Script for evaluating portus with options and kodkod
    ./eval_portus.py --help to see options
"""

import subprocess
import os
import logging
import shutil

from testrunner import testrunner as tr
from testrunner import util 
import argparse
from typing import *

from setup_scripts.config import needed_names_file, models_dir, models_command_file, ALLOY_JAR, models_dir

ALLOY_JAR_DEFAULT = ALLOY_JAR 


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
models_and_cmds = tr.CSVOption('models_and_cmds', models_command_file)



methods = util.PORTUS_METHODS
method_names = list(methods.keys())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='portus tests',
        description='An evaluation script for Portus'
    )
    
    parser.add_argument('-t', '--timeout',
                        type=int, default=30*60,
                        help='timeout for each model in seconds (default: %(default)s)')
    parser.add_argument('-o', '--output',
                    type=str,
                    default=None,
                    help="file to write the csv file out to. (default: test-date-stamp-tumbo-notexclusive.csv')")
    parser.add_argument('-v', '--verbose',
                        action='store_true')
    
    methods_group = parser.add_mutually_exclusive_group(required=False)
    
    methods_group.add_argument('-m', '--methods',
                        nargs='+', type=str,
                        choices=method_names,
                        default=['portus'],
                        help='methods to run e.g., portus kodkod (no commas) (default: portus)',
                        )
    methods_group.add_argument('--all-methods', help='use all methods', action='store_true')
    
    
    scopes_group = parser.add_mutually_exclusive_group(required=False)
    scopes_group.add_argument('--scopes',
                        nargs='+', type=int,
                        default=[2,4,8,16,32],
                        help='scopes at which to test (default: 2 4 8 16 32)'
                        )
    scopes_group.add_argument('--default-scopes', action='store_false', help='use scopes defined in the files')

    parser.add_argument('--alloy-jar',
                        default=ALLOY_JAR_DEFAULT,
                        help='path to the alloy jar (default: %(default)s)'
                        )
    parser.add_argument('--corpus-root',
                        default=os.path.dirname(os.path.abspath(models_dir)),  # Remove top-level folder name
                        help='directory containing the expert models (default derived from ./config.py: %(default)s)')
    
    
    rerun_group = parser.add_argument_group('re-run adjustments')
    
    rerun_group.add_argument('-i', '--iterations',
                        type=int, default=1,
                        help='number of iterations to run each set of arguments (default: %(default)s)')
    rerun_group.add_argument('-s', '--skip',
                        type=int, default=0,
                        help='number of values to skip (default: %(default)s)')
    rerun_group.add_argument('--force-header', action='store_true',
                        help='forces the header to be written to the output file')
    
    parser.add_argument('-e','--exclusive',
                        action='store_true',
                        help='whether this process has exclusive use of CPU (written into output file name)')

    parser.add_argument('-c','--computer',
                        default="tumbo",
                        help="name of processor being used (written into output file name)")
    
    parser.add_argument('--memory',
                        type=str, default='30g',
                        help='Amount of memory for java to allocate using -Xmx and -Xms (default: %(default)s)')

    args = parser.parse_args()
    
    if args.all_methods:
        args.methods = method_names
    
    output_file_name = ""
    if args.output == None:
        if (args.exclusive):
            output_file_name = f'test-{util.now_string()}-{args.computer}-exclusive.csv' 
        else: 
            output_file_name = f'test-{util.now_string()}-{args.computer}-notexclusive.csv' 
    else:
        output_file_name = args.output


    if args.verbose:
        print("Arguments:\n")
        print("corpus_root= "+str(args.corpus_root))
        print("input file= "+ models_command_file)
        print("output file= "+str(output_file_name)+"\n")
        print("all_methods= "+str(args.all_methods))
        print("methods= "+str(args.methods)+"\n")
        print("alloy_jar= " + str(args.alloy_jar)+"\n")
        print("default_scopes= "+str(args.default_scopes) + " (irrelevant if default_scopes is true)")
        print("scopes= "+str(args.scopes)+"\n")
        print("timeout= "+str(args.timeout))
        print("iterations= "+str(args.iterations))
        print("skip= "+str(args.skip)+"\n")
        print("force_header= "+str(args.force_header)+"\n")
        print("verbose= " + str(args.verbose) + " (if true, log file is also created)")
        #print(f'{args=}')
    
    # command = f'java -cp {args.alloy_jar} {args.portus_jar} {{method_args}} {{model}}'
    # command = f'java -Xmx30g -Xms30g -cp {args.alloy_jar} ca.uwaterloo.watform.portus.cli.PortusCLI {{method_args}} -all-scopes {{scope}} -command {{command_number}} {args.corpus_root}/{{model}}'
    command = f'{shutil.which("java")} -Xmx{args.memory} -Xms{args.memory} -cp {args.alloy_jar} ca.uwaterloo.watform.portus.cli.PortusCLI {{method_args}} -all-scopes {{scope}} -command {{command_number}} {args.corpus_root}/{{model}}'

    result_fields = ['return_code', 'time_elapsed']
    ignore_fields = ['method_args']
    
    if args.default_scopes:
        #command = f'java -Xmx30g -Xms30g -cp {args.alloy_jar} ca.uwaterloo.watform.portus.cli.PortusCLI {{method_args}} -command {{command_number}} {args.corpus_root}/{{model}}'
        command = f'{shutil.which("java")} -Xmx{args.memory} -Xms{args.memory} -cp {args.alloy_jar} ca.uwaterloo.watform.portus.cli.PortusCLI {{method_args}} -command {{command_number}} {args.corpus_root}/{{model}}'
        args.scopes = [8]  # This should just be a default value so we don't run commands multiple times
    
    # Generate options for methods chosen
    # Create the lined options 'method' and 'method_args'
    methods_used = {key: methods[key] for key in args.methods}
    method_options = [{'method': method, 'method_args': method_args} for (method, method_args) in methods_used.items()]
    
    method_opt = tr.Option('method_opt',method_options)
    
    scope_opt = tr.Option('scope', args.scopes)
    
    with open(output_file_name,'w') as output_file:
        runner = tr.CSVTestRunner(command,
            scope_opt, models_and_cmds, method_opt, 
            timeout=args.timeout,
            output_file=output_file,
            result_fields=result_fields,
            fields_from_result=result_values,
            fields_from_timeout=timeout_values,
            ignore_fields=ignore_fields,
        )
        
        if args.verbose:
            util.setup_logging_debug()
        else:
            util.setup_logging_default()
        
        runner.run(args.iterations, args.skip, args.force_header)
