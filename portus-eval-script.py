"""
    alternative script for portus evaluation
    where we just set the values in the script.

"""

import logging
import subprocess
import psutil
import shutil
from pathlib import Path 

import testrunner.testrunner as tr
import testrunner.util as util

# --- main options that change

# Timeout in seconds
TIMEOUT: int = 60 * 60  # 60 mins

# how many times do we want to run each command?
ITERATIONS = 3

# To resume in the middle of an execution
SKIP = 0  # number of iterations to skip

filename_suffix = "-datatypes-evaluate-z3-larger-timeout"

def command(alloy_jar,portus_jar):
    return f'{shutil.which("java")} -Xmx30g -Xms30g -cp {alloy_jar} {portus_jar} {{method_args}} -compiler {{compiler}} -solver {{solver}} -nt -command {{command_number}} {{model}}'

compiler: tr.Option = tr.Option('compiler', [
    "Standard",
    "DatatypeWithRangeEUF",
    "DatatypeNoRangeEUF",
    "Evaluate",
    "EvaluateQDef",

])

solver: tr.Option = tr.Option('solver', [
    "Z3NonIncCli",
])

# this one has more work before it becomes just an option to the command
methods = ['portus-full']

# ------ below this line is unlikely to change

models_command_file="models-supported-command.txt"
models_and_cmds = tr.CSVOption('models_and_cmds', models_command_file)

ALLOY_JAR = Path('../org.alloytools.alloy/org.alloytools.alloy.dist/target/org.alloytools.alloy.dist.jar')
PORTUS_JAR = 'ca.uwaterloo.watform.portus.cli.PortusCLI'

# mapping from method names to portus options
# Include -b to increase bitwidth as required
# For correctness, use -c instead of -r
PORTUS_METHODS = {
    'kodkod': '-rk',
    'portus-full': '-r',
    'portus-minus-partition-mem-pred': '-r -disable-partition-sp -disable-mem-pred-opt',
    'portus-minus-scalar': '-r -disable-simple-scalar-opt -disable-one-sig-opt -disable-join-opt',
    'portus-minus-functions': '-r -disable-func-opt',
    'portus-minus-constants-axioms': '-r -b -use-card-sap',
    'unoptimized': '-r -disable-all-opts -disable-func-opt -b -use-card-sap',
    'claessen': '-r -compiler constants-claessen',
}
# Generate options for methods chosen
# Create the lined options 'method' and 'method_args'
methods_used = {key: PORTUS_METHODS[key] for key in methods}
method_options = [{'method': method, 'method_args': method_args} for (method, method_args) in methods_used.items()]

method_opt = tr.Option('method_opt',method_options)

def output_file_name(filename_suffix): 
    return f'{util.now_string()}{filename_suffix}-results.csv'

FORCE_HEADER = False # rewrite the csv header

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
    util.kill_solvers()
    return results

# Fill in result fields when the process times out
# same arguments as above except for timeout
# returns a dictionary with values for results_fields above
def timeout_values(opts: tr.OptionDict, result: subprocess.TimeoutExpired) -> tr.OptionDict:
    logging.info('Timed out.')
    results: tr.OptionDict = {
        'return_code': 999,
        'time_elapsed': -1,  # the actual value for the timeout limit was an option input
        'satisfiability': 'UNKNOWN',
    }
    # Ensure no active child processes; Z3 does not always quit when
    # parent process timeouts
    util.kill_solvers()
    return results

result_fields = ['return_code', 'time_elapsed', 'satisfiability']
ignore_fields = []

# option with only one value, but it gets it printed in the output
# it is not used in the command
timeout: tr.Option = tr.Option('timeout', [TIMEOUT])

# Level of debug
util.setup_logging_debug(filename_suffix)
# or:
#util.setup_logging_default()

# This is the call to the CSVTestRunner to execute the runs
# Remember to list the options here
with open(output_file_name(filename_suffix), 'w') as output_file:
    runner = tr.CSVTestRunner(
        command(ALLOY_JAR, PORTUS_JAR),  # command string with blanks to fill in
        models_and_cmds,
        method_opt,
        compiler, # option
        solver, # option
        timeout, # unused option but gets it included in a table of the output
        timeout=TIMEOUT,
        output_file=output_file,
        fields_from_result=result_values, # how to interpret results of run
        fields_from_timeout=timeout_values,   # how to interpret timeouts
        # output CSV file contains all non_ignored fields
        result_fields = result_fields,
        ignore_fields=ignore_fields,
    )  
    runner.run(ITERATIONS, SKIP, FORCE_HEADER)
