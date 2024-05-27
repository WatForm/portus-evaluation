# README.md

Below we describe how to execute the evaluation we ran for our paper.

1.  Setup - run `make` to set up the models.  The Makefile does the following:

    a) Create the expert-models directory and download the expert models into that directory
    These models are the set of expert-models chosen for the paper:
    Elias Eid and Nancy A. Day. Static profiling Alloy models. IEEE Transactions on Software Engineering (IEEE TSE), 49(2):743--759, February 2023. [https://ieeexplore.ieee.org/document/9744446] 

    b) Remove unneeded, non-Alloy files

    c) Update the syntax used in these models for Alloy 6

    d) Remove expert models that Portus does not support (for reasons listed in comments in this script)

    e) Create a txt file with a list of the top-level .als files supported in models-supported.tzt

    At any point you can wipe out all downloaded/generated files via `make clean`.

3. Environment Setup

    a) install a command-line version of Z3, version 4.8.15 or higher.
    Binaries are available [https://github.com/Z3Prover/z3/releases].
    If using MacOS, we recommend using Homebrew: `brew install z3`.
    If on Ubuntu, do not use apt-get, since its version of Z3 is out of date.
    We have not successfully built fortress on Windows yet, however, if built elsewhere the jars should work on Windows.

    b) Install the sbt build tool [https://www.scala-sbt.org/]

3. Build portus branch of Alloy with fortress: put it in a **sibling** to this folder
    `cd ..`
    `git clone https://github.com/WatForm/org.alloytools.alloy.git`
    `cd org.alloytools.alloy`
    `git checkout portus`
    `git submodule init`
    `git submodule update`      -- must be done after checked out portus branch
    `jenv local 12`             -- set the version of Java to be 12 by some method
    `./gradlew build`
    `cd ../portus-evaluation`

5. Install Python 3.8.8+ (or higher) and the psutil and tqdm packages for python3 possibly using a virtual environment as in:
    `python3 -m venv venv`       -- creates a directory called venv for a virtual python env 
    `source venv/bin/activate`   -- activates virtual environment
    `pip3 install -r requirements.txt` -- installs python dependencies in venv

    At any point you can leave this virtual environment using `deactivate`

6. Run various executions of portus and kodkod in the virtual environment.  The python script eval_portus.py has lots of options.  Each execution of the script runs specified versions of portus and/or kodkod on the expert-models a certain number of iterations with a timeout and outputs the times to a .csv output file.

    `source venv/bin/activate`  - to restart the virtual environment
    `python3 eval_portus.py --help` shows the configuration options

    - The options `--alloy-jar` and `--corpus-root` set the location of the portus jar and the repository of expert models.  If you built portus in a sibling folder called `portus`, you can use the default value for `--alloy-jar` (`../org.alloytools.alloy.dist/target/org.alloytools.alloy.dist.jar`).  If you followed step 1, you can use the default value for `--corpus-root` (`./expert-models`)
    
7. Here are the tests we ran:
    `python3 eval_portus.py -m portus kodkod`
    ...