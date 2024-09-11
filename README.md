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

2.  Setup - run `make` to set up the models.  The Makefile does the following:

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

3. Environment Setup

    a) install a command-line version of Z3, version 4.8.15 or higher.
    Binaries are available [https://github.com/Z3Prover/z3/releases].
    If using MacOS, we recommend using Homebrew: `brew install z3`.
    If on Ubuntu, do not use apt-get, since its version of Z3 is out of date.
    We have not successfully built fortress on Windows yet, however, if built elsewhere the jars should work on Windows.

    b) Install the sbt build tool [https://www.scala-sbt.org/]

4. Build portus branch of Alloy with fortress: put it in a **sibling** to this folder
   TODO: make this downloading a .jar release
```bash
cd ..
git clone https://github.com/WatForm/org.alloytools.alloy.git
cd org.alloytools.alloy
# checkout the portus branch
git checkout portus
git submodule init
# must be done after checking out portus branch; rerun this if there is an update to fortress
git submodule update --recursive --remote
# set the version of Java to be 12 (or higher) by some method
jenv local 12
# necessary if submodule has been updated
./gradlew clean
./gradlew build
cd ../portus-evaluation
```

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

# Section 6.2, Performance of Portus optimizations and Section 6.3, Performance compared to Kodkod
# Outputs:
#   test-<timestamp>-tumbo-notexclusive.csv: CSV of each method's time and satisfiability result
#     for each (model, command) pair in models-supported-command.txt
python3 eval_portus.py -m portus-full kodkod kodkod-minisat portus-minus-partition-mem-pred portus-minus-scalar portus-minus-constants-axioms -i 3 -t 300
# NOTE: portus-minus-scalar is expected to fail on the following two models:
#  expert-models/3zltn65gds66b6f4q3lvbtgdkb6snmuu-alloy/hc-atd/converge.als
#  expert-models/7z32luflamhdcixvt6nwznnud4oi6dbr-MSV/CaseStudies/OLAPUsagePrefs/OLAPUsagePrefs.als
# This is because certain integer expressions used in these models require the scalar optimizations enabled
# for Portus to be able to translate them. See Section 4.2 in the paper.

# Section 6.4, Scalability, research question 1 (benchmark set)
# Outputs:
#   scale-benchmark-set-kodkod.csv: CSV of Kodkod's times for each (model, command, sig) tuple,
#     scaling the scope from 2 to 80 with step 2
#   worst-scaling-sigs.txt: list of the worst-scaling sigs for each (model, command) pair
#   scale-benchmark-set-portus.csv: CSV of Portus's times for each (model, command, sig) tuple in worst-scaling-sigs.txt,
#     scaling the scope from 2 to 80 with step 2
python3 -m scaling_eval --models models-supported-command.txt --methods kodkod --start 2 --end 80 --step 2 --timeout 300 --out scale-benchmark-set-kodkod.csv
python3 scaling_eval/select_worst.py scale-benchmark-set.csv worst-scaling-sigs.txt
python3 -m scaling_eval --models models-supported-command.txt --methods portus-full --start 2 --end 80 --step 2 --timeout 300 --out scale-benchmark-set-portus.csv

# Section 6.4, Scalability, research question 2 (language feature models)
# Outputs:
#   scale-language-feature-models.csv: CSV of Kodkod and Portus's times for each (model, command, sig) tuple,
#     scaling the scope from 2 to 80 with step 2
python3 -m scaling_eval --models language-feature-models/models-command.txt --start 2 --end 80 --step 2 --timeout 300 --out scale-language-feature-models.csv
```

The `eval_portus.py` and `scaling_eval` scripts have lots of options. Running `python3 eval_portus.py --help` and `python3 -m scaling_eval --help` will show the options. In particular, for both scripts, the options `--alloy-jar` and `--corpus-root` set the location of the portus jar and folder containing the repository of expert models, respectively.  If you built portus in a sibling folder called `portus`, you can use the default value for `--alloy-jar` (`../org.alloytools.alloy.dist/target/org.alloytools.alloy.dist.jar`).  If you followed step 1, you can use the default value for `--corpus-root` (the current directory).
