#!/usr/bin/env python

"""
After running the previous scripts, we are left with the files for
a number of models.  
This script makes a txt file listing the top-level .als files of the 
models that Portus supports
and it removes any model files that we don't need.
"""

import os
import os.path  

from config import needed_names_file, models_dir, models_supported_file

# read the filenames-of-all-parts-expert-models.txt
# top-level filename is dictionary key matched with false
# in another dictionary every filename is matched with a top-level filename
top_level_model_files = {}
all_model_files = {}
with open(needed_names_file, 'r') as models:
	for m in models:
		# this gets us a comma-separated list of related files
		fs = m.split(",")
		model_file = fs[0].strip()
		top_level_model_files[model_file] = False
		for k in fs:
			all_model_files[k.strip()] = model_file
			#print(k.strip() + " - "+ model_file)

# read the files in the directory
# iterate through it first to see which top-level models have been kept
# and set the Boolean true for those kept
for root, dirs, files in os.walk(models_dir):
	for f in files:
		filename = str(os.path.join(root, f))
		#print(filename)
		if (filename in top_level_model_files.keys()):
			# print("accept: "+filename+"\n")
			top_level_model_files[filename] = True
			#print("FOUND: "+filename)

# iterate through it a second time
# to keep only those files used by kept top-level models
for root, dirs, files in os.walk(models_dir):
	for f in files:
		filename = str(os.path.join(root, f))
		if not (".git" in filename):
			if (filename in all_model_files.keys()):
				top_level_model_file = all_model_files[filename]
				if not(top_level_model_files[top_level_model_file]):
					# it's not a file we need to keep
					#print("REJECT: "+filename)
					os.remove(filename)
			else:
				print("Error: "+filename+ " is not a model file")
				exit(1)

# create the txt file with the names of the top level models that we support

with open(models_supported_file, 'w') as models_supported:
	for f in top_level_model_files.keys():
		if (top_level_model_files[f]):
			models_supported.write(f+"\n")
models_supported.close()