#!venv/bin/python3

import subprocess
import os
import shutil 

CMD="/Users/nday/.jenv/shims/java -Xmx30g -Xms30g -cp ../org.alloytools.alloy/org.alloytools.alloy.dist/target/org.alloytools.alloy.dist.jar ca.uwaterloo.watform.portus.cli.PortusCLI -smtlib-tc -nt -command"

models_dir = "expert-models/"
expert_models = "models-supported-command.txt"
smttc_dir = "smttc"

if __name__ == '__main__':

    with open(expert_models, 'r') as f:
        files = f.readlines()
        skip_first = True
        for file_name_cmd in files:
            if skip_first:
                skip_first=False
            else:
                split = file_name_cmd.split(',')
                file_name = split[0].strip()
                cmd_num = split[1].strip()      # Alloy cmd number to run
                cmd_to_run = CMD+" "+cmd_num+" "+ file_name
                print(cmd_to_run)
                # set check=True to stop when return code != 0
                subprocess.run([cmd_to_run],text=True,check=True,capture_output=True,shell=True)

    # collect the smtc files - they are created right beside the .als file
    if not(os.path.exists(smttc_dir)):
        os.mkdir(smttc_dir)
    for dpath, dnames, fnames in os.walk(models_dir):
        for fname in fnames:
            if fname.endswith(".smttc"):
                #print(dpath+"/"+fname)
                print(smttc_dir +"/"+fname)
                shutil.copy(dpath+"/"+fname, smttc_dir+"/"+fname)