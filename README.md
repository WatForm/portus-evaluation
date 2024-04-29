# portus-tests

1. Run the script get-expert-models.sh to download the expert models.

2. Update the syntax used in these models for Alloy 6
    
    `find . -name "*.als" | xargs sed '' "s/'/\"/g"` (on Mac)

4. Build Portus 
    - (cloning and buliding it in a folder called `portus` that is a sibling to this folder will simplify steps later)

5. Install Python 3.8.8+ and the packages in `requirements.txt`
    - We suggest venv to manage a virtual environment

6. Run `python3 eval_portus.py --help` to look at all the configuration options
    - Pay particular attention to `--alloy-jar` and `--corpus-root` as they will depend on your installation
    - If you built portus in a sibling folder called `portus`, you can use the default value for `--alloy-jar` (`../portus/org.alloytools.alloy.dist/target/org.alloytools.alloy.dist.jar`)
    - If you followed steps 1-2, you can use the default value for `--corpus-root` (`.`)
7. Run a test
    - A simple test comparing kodkod and portus is `python3 eval_portus.py -m portus kodkod`. 
    - If you are unable to use the default values, also provide the `--alloy-jar` and `--corpus-root` arguments. e. g. `python3 eval_portus.py -m portus kodkod --corpus-root ~/portus-corpus --alloy-jar ~/org.alloytools.alloy.dist.jar`