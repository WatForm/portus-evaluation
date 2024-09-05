#!venv/bin/python3

"""
    Script for evaluating portus with options and kodkod
    ./eval_portus.py --help to see options

    Methods:
    kodkod: run Kodkod
    portus-full: run Portus with all optimizations
    portus-minus-partition-mem-pred: run Portus with all optimizations except the partition sort policy/membership predicate optimization
    portus-minus-scalar: run Portus with all optimizations except the simple scalar, one sig, and join optimizations
    portus-minus-functions: run Portus with all optimizations except the function optimization
    portus-minus-constants-axioms: run Portus with all optimizations except use the cardinality-based scope axioms instead of the constants scope axioms
    unoptimized: run Portus with no optimizations
    claessen: run Portus with all optimizations and the constants-claessen compiler (using Claessen TC instead of Eijck)

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

import psutil

# Include -b to increase bitwidth as required
# For correctness, use -c instead of -r
PORTUS_METHODS = {
    'kodkod': '-rk', # sat4j
    'kodkod-minisat': '-rk-ms',
    'portus-full': '-r',
    'portus-minus-partition-mem-pred': '-r -disable-partition-sp -disable-mem-pred-opt',
    'portus-minus-scalar': '-r -disable-simple-scalar-opt -disable-one-sig-opt -disable-join-opt',
    'portus-minus-functions': '-r -disable-func-opt',
    'portus-minus-constants-axioms': '-r -b -use-card-sap',
    'unoptimized': '-r -disable-all-opts -disable-func-opt -b -use-card-sap',
    'claessen': '-r -compiler constants-claessen',
}

ALLOY_JAR_DEFAULT = ALLOY_JAR 
TIMEOUT_DEFAULT = 5*60

# Kill lingering Z3 processes
def kill_z3():
    for proc in psutil.process_iter():
        try:
            if 'z3' in proc.name().lower():
                # We found a z3 process
                logging.warn('Z3 is still running... killing')
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    


# Fill in result fields when the process completes
def result_values(opts: tr.OptionDict, result: subprocess.CompletedProcess, time_elapsed: float) -> tr.OptionDict:
    if result.returncode != 0:
        logging.error('------OUTPUT------\n' + result.stdout + '------STDERR-----\n' + result.stderr +"------------")
    satisfiability: str = 'UNKNOWN'

    if result.returncode == 0:
        if 'Result: SAT' in result.stdout:
            satisfiability = 'SAT'
        elif 'Result: UNSAT' in result.stdout:
            satisfiability = 'UNSAT'
    # returning fields for output
    results: tr.OptionDict = {
        'return_code': result.returncode,
        'time_elapsed': time_elapsed,
        'satisfiability': satisfiability
    }

    # Ensure no active z3 processes
    kill_z3()
    return results

# function for how to deal with timeout values
# Fill in result fields when the process times out
def timeout_values(opts: tr.OptionDict, result: subprocess.TimeoutExpired) -> tr.OptionDict:
    logging.info('Timed out.')
    results: tr.OptionDict = {
        'return_code': 999,
        'time_elapsed': -1,
        'satisfiability': 'UNKNOWN',
    }
    # Ensure no active z3 processes
    kill_z3()
    return results




# models = tr.FromFileOption('model', 'expert-models-list.txt')
models_and_cmds = tr.CSVOption('models_and_cmds', models_command_file)



methods = PORTUS_METHODS
method_names = list(methods.keys())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='portus tests',
        description='An evaluation script for Portus'
    )
    
    parser.add_argument('-t', '--timeout',
                        type=int, default=TIMEOUT_DEFAULT,
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
                        default=['portus-full'],
                        help='methods to run e.g., portus-full kodkod (no commas) (default: %(default)s)',
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
        print("default_scopes= "+str(args.default_scopes) )
        print("scopes= "+str(args.scopes)+ " (irrelevant if default_scopes is true)\n")
        print("timeout= "+str(args.timeout))
        print("iterations= "+str(args.iterations))
        print("skip= "+str(args.skip)+"\n")
        print("force_header= "+str(args.force_header)+"\n")
        print("verbose= " + str(args.verbose) + " (if true, log file is also created)")
        #print(f'{args=}')
    
    # command = f'java -cp {args.alloy_jar} {args.portus_jar} {{method_args}} {{model}}'
    # command = f'java -Xmx30g -Xms30g -cp {args.alloy_jar} ca.uwaterloo.watform.portus.cli.PortusCLI {{method_args}} -all-scopes {{scope}} -command {{command_number}} {args.corpus_root}/{{model}}'
    command = f'{shutil.which("java")} -Xmx{args.memory} -Xms{args.memory} -cp {args.alloy_jar} ca.uwaterloo.watform.portus.cli.PortusCLI {{method_args}} -nt -all-scopes {{scope}} -command {{command_number}} {args.corpus_root}/{{model}}'

    result_fields = ['return_code', 'time_elapsed', 'satisfiability']
    ignore_fields = ['method_args']
    
    if args.default_scopes:
        #command = f'java -Xmx30g -Xms30g -cp {args.alloy_jar} ca.uwaterloo.watform.portus.cli.PortusCLI {{method_args}} -command {{command_number}} {args.corpus_root}/{{model}}'
        # double bracketing things keep the brackets and are therefore options to the command for the TestRunner
        command = f'{shutil.which("java")} -Xmx{args.memory} -Xms{args.memory} -cp {args.alloy_jar} ca.uwaterloo.watform.portus.cli.PortusCLI {{method_args}} -nt -command {{command_number}} {args.corpus_root}/{{model}}'
        args.scopes = [-1]  # This should just be a default value so we don't run commands multiple times
    
    # Generate options for methods chosen
    # Create the linked options 'method' and 'method_args'
    methods_used = {key: methods[key] for key in args.methods}
    method_options = [{'method': method, 'method_args': method_args} for (method, method_args) in methods_used.items()]
    
    method_opt = tr.Option('method_opt',method_options)
    
    scope_opt = tr.Option('scope', args.scopes)
    
    with open(output_file_name,'w') as output_file:
        print("Output file: "+output_file_name)
        runner = tr.CSVTestRunner(command,
            scope_opt, models_and_cmds, method_opt, 
            timeout=args.timeout,
            output_file=output_file,
            result_fields=result_fields,
            fields_from_result=result_values,
            fields_from_timeout=timeout_values,
            # output CSV file contains all non_ignored fields
            ignore_fields=ignore_fields,
            clear_cache=True
        )
        
        if args.verbose:
            util.setup_logging_debug()
        else:
            util.setup_logging_default()
        
        runner.run(args.iterations, args.skip, args.force_header)
