#!/usr/bin/env python

"""
This script is run after the expert models have been downloaded. 
Because the entire repositories are downloaded by the git clones, we want 
to filter the files and end up with just the needed top-level models and
any supporting files that they import.

The file filenames-of-all-parts-of-expert-models.txt
from Elias contains the names of all needed files and only those.
"""

import os
import os.path  

from config import needed_names_file, models_dir

# read and put in a dictionary needed_names_files with a Boolean to say
# not yet found
found_file = {}
with open(needed_names_file, 'r') as models:
	for m in models:
		# this gets us a comma-separated list of related files
		fs = m.split(",")
		for k in fs:
			found_file[k.strip()] = False
			#print(k.strip())

# iterate through all files in models directory and remove any
# that are not in the dictionary and if found then set Boolean to true
for root, dirs, files in os.walk(models_dir):
	for f in files:
		filename = str(os.path.join(root, f))
		if not (".git" in filename):
			if (filename in found_file.keys()):
				found_file[filename] = True
				#print("accept: "+filename+"\n")
			else:
				os.remove(filename)
				#print("reject: "+filename+"\n")

# output any needed files that are not found
for a in found_file.keys():
	if not(found_file[a]):
		print(a + " not found")


