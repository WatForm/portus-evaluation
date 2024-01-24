import os
import shlex
import subprocess
import argparse
import random


DEFAULT_SEED = 1

parser = argparse.ArgumentParser()
mode_group = parser.add_mutually_exclusive_group(required=True)
mode_group.add_argument('--all', '-a', action='store_true', help='Run every command for every file')
mode_group.add_argument('--random', '-r', type=int, nargs='?', default=DEFAULT_SEED, help='Randomly select a single command using the provided seed')

args = parser.parse_args()

# This file is used to update expert-models.csv when the models listed in
# expert-models-list.txt is changed
# It counts the number of commands present in the file so we can select one at random

MODELS_LIST = "expert-models-list.txt"
OUTPUT_TARGET = "expert-models.csv"

ALLOY_JAR = '../portus/org.alloytools.alloy.dist/target/org.alloytools.alloy.dist.jar'

PORTUS_JAR = 'ca.uwaterloo.watform.portus.cli.PortusCLI'

command = f'java -cp {ALLOY_JAR} {PORTUS_JAR} -r -compiler constants -command 999 {{model}}'

PREFIX = "Error: command number 999 is too large, there are only "

seed = args.random if args.random is not None else DEFAULT_SEED
random.seed(seed)

with open(MODELS_LIST, 'r') as models, open(OUTPUT_TARGET, '+w') as output:
    print('model,command_number', file=output)
    
    for model in models:
        model = model[:-1]  # remove newline
        cmd = command.format(model=model)
        cmd = shlex.split(cmd)
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        cmd_count = None
        for line in result.stderr.splitlines():
            if line.startswith(PREFIX):
                line = line[len(PREFIX):]
                cmd_count = int(line.split()[0])
        
        if cmd_count is None:
            continue
        if args.all:
            for i in range(1,cmd_count+1):
                print(f'{model}, {i}', file=output)
        else:
            # Pick a single random range
            command_chosen = random.randint(1,cmd_count)
            print(f'{model}, {command_chosen}', file=output)
        
        
        
            
