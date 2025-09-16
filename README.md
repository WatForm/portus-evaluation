# README.md

Below we describe how to execute the evaluation we ran for our paper.  

We assume the following are already installed:
- python 3 (version 3.8.8 or higher), venv
- Java version 12
- make
- git
- find, sed, and regular command-line utilities

1.  Setup this repository: clone [https://github.com/WatForm/testrunner] within this repository.
```bash
git clone https://github.com/WatForm/testrunner.git
```

2. Environment Setup

    a) Install a command-line version of Z3, version 4.8.15 or higher.
    Z3 version 4.13.0 was used for our evaluation.
    Binaries are available [https://github.com/Z3Prover/z3/releases].
    If using MacOS, we recommend using Homebrew: `brew install z3`.
    If on Ubuntu, do not use apt-get, since its version of Z3 is out of date.
    We have not successfully built fortress on Windows yet, however, if built elsewhere the jars should work on Windows.

    b) Install CVC5, version 1.1.2 or higher (https://cvc5.github.io).
    CVC5 version 1.1.2 was used for our evaluation.

    c) Install the sbt build tool [https://www.scala-sbt.org/]

3. Download the [Portus v1.0.2 JAR](https://github.com/WatForm/org.alloytools.alloy/releases/download/portus-v1.0.2/portus.jar) and put it in this folder:
```bash
wget https://github.com/WatForm/org.alloytools.alloy/releases/download/portus-v1.0.2/portus.jar
```
Alternatively, build the `portus` branch of our fork of Alloy with Fortress as follows:
```bash
cd ..
git clone https://github.com/WatForm/org.alloytools.alloy.git
cd org.alloytools.alloy
# checkout the portus branch
git checkout portus
git submodule init
# must be done after checking out portus branch; rerun this if there is an update to fortress
git submodule update --recursive --remote
# cleaning is necessary if submodule has been updated
./gradlew clean
./gradlew build
cd ../portus-evaluation
cp ../org.alloytools.alloy/org.alloytools.alloy.dist/target/org.alloytools.alloy.dist.jar portus.jar
```

4.  Setup - run `make` to set up the models.  The Makefile does the following:

    a) Create the expert-models directory and download the expert models into that directory
    These models are the set of expert-models chosen for the paper:
    Elias Eid and Nancy A. Day. Static profiling Alloy models. IEEE Transactions on Software Engineering (IEEE TSE), 49(2):743--759, February 2023. [https://ieeexplore.ieee.org/document/9744446] 

    b) Remove unneeded, non-Alloy files

    c) Update the syntax used in these models for Alloy 6

    d) Remove expert models that Portus does not support (for reasons listed in comments in this script)

    e) Create a txt file with a list of the top-level .als files supported in models-supported.txt

    f) Create a txt file with a list of the supported top-level .als files, cmd# in models-supported-command.txt (this requires Alloy/Portus to have been built)

    At any point you can wipe out all downloaded/generated files via `make clean`.

    These instructions should work for Mac OS and Linux.  The fix-models.sh script used in the Makefile will probably *not* work under Windows, but most other scripts should be robust.

5. Create a virtual environment as in:
```bash
# creates a directory called venv for a virtual python env
python3 -m venv venv
# activates virtual environment
source venv/bin/activate
# installs python dependencies in venv
python -m pip install -r requirements.txt
# exit the virtual env
deactivate
```
The virtual environment can be removed at any time using `rm -rf venv`.

6. Here are the tests we ran:
```bash
# Enter the virtual environment
source venv/bin/activate

# Section 5.2, Performance of Portus optimizations and Section 5.3, Performance compared to Kodkod
# Outputs:
#   test-<timestamp>-tumbo-notexclusive.csv: CSV of each method's time and satisfiability result
#     for each (model, command) pair in models-supported-command.txt
python3 eval_portus.py -m portus-full portus-full-cvc5 kodkod kodkod-minisat portus-minus-partition-mem-pred portus-minus-scalar portus-minus-constants-axioms -i 3 -t 300

# Section 5.4, Scalability, research question 1 (benchmark set)
# Outputs:
#   scale-benchmark-set-kodkod.csv: CSV of Kodkod's times for each (model, command, sig) tuple,
#     scaling the scope from 2 to 80 with step 2
#   worst-scaling-sigs.txt: list of the worst-scaling sigs for each (model, command) pair
#   scale-benchmark-set-portus.csv: CSV of Portus's times for each (model, command, sig) tuple in worst-scaling-sigs.txt,
#     scaling the scope from 2 to 80 with step 2
# Scale all signatures in all models with Kodkod.
python3 -m scaling_eval --models models-supported-command.txt --methods kodkod --start 2 --end 80 --step 2 --timeout 300 --repeat 1 --out scale-benchmark-set-kodkod.csv
# Select the worst-scaling signature according to Kodkod from each model and output it to worst-scaling-sigs.txt in CSV format.
# Note that depending on the exact conditions on your machine, this could select different sigs from those used in the paper!
# The worst-scaling sigs used in the paper are found in worst-scaling-sigs-ours.txt.
python3 scaling_eval/select_worst.py scale-benchmark-set-kodkod.csv worst-scaling-sigs.txt
# Scale the signatures selected above with Portus.
# To scale the same signatures as used in the paper, specify `--models worst-scaling-sigs-ours.txt` instead.
python3 -m scaling_eval --models worst-scaling-sigs.txt --sigs specified --methods portus-full --start 2 --end 80 --step 2 --timeout 300 --repeat 1 --out scale-benchmark-set-portus.csv

# Section 5.4, Scalability, research question 2 (language feature models)
# Outputs:
#   scale-language-feature-models.csv: CSV of Kodkod and Portus's times for each (model, command, sig) tuple,
#     scaling the scope from 2 to 80 with step 2
python3 -m scaling_eval --models language-feature-models/models-commands.txt --start 2 --end 80 --step 2 --timeout 300 --out scale-language-feature-models.csv
```

The `eval_portus.py` and `scaling_eval` scripts have lots of options. Running `python3 eval_portus.py --help` and `python3 -m scaling_eval --help` will show the options. In particular, for both scripts, the options `--alloy-jar` and `--corpus-root` set the location of the portus jar and folder containing the repository of expert models, respectively. If you followed step 4, you can use the default value for `--alloy-jar` (`./portus.jar`). If you followed step 1, you can use the default value for `--corpus-root` (the current directory).
