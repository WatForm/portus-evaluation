# README.md

Below we describe how to execute the evaluation we ran for our paper.

1.  Setup - run `make` to set up the models.  The Makefile does the following:

    a) Create the expert-models directory and download the expert models into that directory
    via `./get-expert-models.sh`
    These models are the set of expert-models chosen for the paper:
    Elias Eid and Nancy A. Day. Static profiling Alloy models. IEEE Transactions on Software Engineering (IEEE TSE), 49(2):743--759, February 2023. [https://ieeexplore.ieee.org/document/9744446] 

    b) Remove expert models that Portus does not support (for reasons listed in comments in this script) via `./remove-unsupported.sh`

    c) Update the syntax used in these models for Alloy 6 via `cd expert-models; ../fix-models.sh`

2. At any point you can wipe out the set of models via `make clean`.

3. Build portus branch of Alloy: put it in a **sibling** to this folder
    `git clone --recurse-submodules https://github.com/WatForm/org.alloytools.alloy.git`
    `cd org.alloytools.alloy`
    `git checkout portus`
    `git submodule init`
    `git submodule update`
    `./gradlew build`

5. Install Python 3.8.8+ and the packages in `requirements.txt`
    - We suggest venv to manage a virtual environment

6. Run `python3 eval_portus.py --help` to look at all the configuration options
    - Pay particular attention to `--alloy-jar` and `--corpus-root` as they will depend on your installation
    - If you built portus in a sibling folder called `portus`, you can use the default value for `--alloy-jar` (`../portus/org.alloytools.alloy.dist/target/org.alloytools.alloy.dist.jar`)
    - If you followed steps 1-2, you can use the default value for `--corpus-root` (`.`)
    
7. Run a test
    - A simple test comparing kodkod and portus is `python3 eval_portus.py -m portus kodkod`. 
    - If you are unable to use the default values, also provide the `--alloy-jar` and `--corpus-root` arguments. e. g. `python3 eval_portus.py -m portus kodkod --corpus-root ~/portus-corpus --alloy-jar ~/org.alloytools.alloy.dist.jar`