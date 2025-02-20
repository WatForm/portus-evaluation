# Results of test_alloy2smt.py

Instructions for generating these results are in test_alloy2smt.py

## Results

total files: 74

### alloy2smt translating to smt2 file:
file cannot be found: 12 (see below)
java.lang.UnsupportedOperationException: 25
java.lang.RuntimeException: 1
java.lang.IndexOutOfBoundsException: 1
other error: 0
supported to translate to cvc: 35

### running cvc4 on 35 supported files from above:
cvc4 unsupported: 0
cvc4 error: 0
cvc4 unknown: 25
cvc4 sat: 10
cvc4 unsat: 0


## File not found

Ran alloy2smt on all these models in their own directories and still can't find subfiles in the same directory.

expert-models/2scxlb3tbo5bmvmwplglqils7a5uarmx-talks/scc_mp.als
expert-models/3zltn65gds66b6f4q3lvbtgdkb6snmuu-alloy/fullsub2.als
expert-models/3zltn65gds66b6f4q3lvbtgdkb6snmuu-alloy/question.als
expert-models/7z32luflamhdcixvt6nwznnud4oi6dbr-MSV/Systems/CD2DBS_keys/dbs_inst.als
expert-models/7z32luflamhdcixvt6nwznnud4oi6dbr-MSV/Systems/CD2DBS_simple/dbs_inst.als
expert-models/7z32luflamhdcixvt6nwznnud4oi6dbr-MSV/Systems/ElevatorSPL/elevator_spl_events.als
expert-models/lkicptlz3eklrbu7ppmltlkebwrvzhdq-zigbee-alloy-svn-to-git/trunk/base/random_event.als
