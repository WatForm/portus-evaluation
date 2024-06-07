# README.md

Below we describe how to execute the evaluation we ran for our paper.  

We assume the following are already installed:
- python 3 (version 3.8.8 or higher), venv
- Java version 12
- make
- git
- find, sed, and regular command-line utilities

1.  Setup - run `make` to set up the models.  The Makefile does the following:

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

2. Environment Setup

    a) install a command-line version of Z3, version 4.8.15 or higher.
    Binaries are available [https://github.com/Z3Prover/z3/releases].
    If using MacOS, we recommend using Homebrew: `brew install z3`.
    If on Ubuntu, do not use apt-get, since its version of Z3 is out of date.
    We have not successfully built fortress on Windows yet, however, if built elsewhere the jars should work on Windows.

    b) Install the sbt build tool [https://www.scala-sbt.org/]

3. Build portus branch of Alloy with fortress: put it in a **sibling** to this folder
   TODO: make this downloading a .jar release
    `cd ..`
    `git clone https://github.com/WatForm/org.alloytools.alloy.git`
    `cd org.alloytools.alloy`
    `git checkout portus`       -- checkout the portus branch
    `git submodule init`
    `git submodule update --recursive --remote` -- must be done after checked out portus branch; rerun this if there is an update to fortress
    `jenv local 12`             -- set the version of Java to be 12 by some method
    `./gradlew clean`      -- necessary if submodule has been updated
    `./gradlew build`
    `cd ../portus-evaluation`


4. Create a virtual environment as in:
    `python3 -m venv venv`       -- creates a directory called venv for a virtual python env 
    `source venv/bin/activate`   -- activates virtual environment
    `python -m pip install -r requirements.txt` -- installs python dependencies in venv
    `deactivate`                    -- exit the virtual env

    The virtual environment can be removed at any time using rm -rf venv 
    The eval_portus.py (used below) script operates in the virtual environment using a shebang #!venv/bin/python3




5. Here are the tests we ran:
    `python3 eval_portus.py -m portus kodkod`
    ...

6. Run various executions of portus and kodkod in the virtual environment.  The python script eval_portus.py has lots of options.  Each execution of the script runs specified versions of portus and/or kodkod on the expert-models a certain number of iterations with a timeout and outputs the times to a .csv output file.

    `./venv/bin/python3 eval_portus.py --help` shows the configuration options

    - The options `--alloy-jar` and `--corpus-root` set the location of the portus jar and the repository of expert models.  If you built portus in a sibling folder called `portus`, you can use the default value for `--alloy-jar` (`../org.alloytools.alloy.dist/target/org.alloytools.alloy.dist.jar`).  If you followed step 1, you can use the default value for `--corpus-root` (`./expert-models`)
    
