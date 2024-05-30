#!venv/bin/python3

"""
    This script creates a file that creates lines of the form:
        top-level model.als,cmd-number
    where cmd-number is a randomly chosen command number within the .als file

    If run with the '-all' option, this script puts all cmds in the file in the list.

    If run with the '--random' option, this script chose a random cmd to put in the file.

    If this script with --random is run again with the same DEFAULT_SEED (below), 
    it will always choose the same command number.
"""

import os
import shlex
import subprocess
import argparse
import random

from config import needed_names_file, models_dir, models_supported_file, models_command_file, ALLOY_JAR, PORTUS_JAR

DEFAULT_SEED = 1

parser = argparse.ArgumentParser()
mode_group = parser.add_mutually_exclusive_group(required=True)
mode_group.add_argument('--all', '-a', action='store_true', help='Run every command for every file')
mode_group.add_argument('--random', '-r', type=int, nargs='?', default=DEFAULT_SEED, help='Randomly select a single command using the provided seed')

args = parser.parse_args()

# when we run portus with '-command n' it runs command n,
# if we run it with a too-high command number (999),
# then we get an error message that tells us how many commands there are in the model

command = f'java -cp {ALLOY_JAR} {PORTUS_JAR} -compiler constants -command 999 {{model}}'

PREFIX = "Error: command number 999 is too large, there are only "

seed = args.random if args.random is not None else DEFAULT_SEED
random.seed(seed)

with open(models_supported_file, 'r') as models, open(models_command_file, '+w') as output:
    print('model,command_number', file=output)
    
    for model in models:
        model = model[:-1]  # remove newline
        cmd = command.format(model=model)
        cmd = shlex.split(cmd)
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(cmd)

        cmd_count = None
        for line in result.stderr.splitlines():
            if line.startswith(PREFIX):
                line = line[len(PREFIX):]
                cmd_count = int(line.split()[0])
        
        print(model)
        print(cmd_count)
        if cmd_count is None:
            continue
        if args.all:
            for i in range(1,cmd_count+1):
                print(f'{model}, {i}', file=output)
        else:
            # Pick a single random range
            command_chosen = random.randint(1,cmd_count)
            print(f'{model}, {command_chosen}', file=output)
        
        
        
            
