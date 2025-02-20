# Results of test_alloy2smt.py

Instructions for generating these results are in test_alloy2smt.py

## Results

total files: 74

### alloy2smt translating to smt2 file:
file cannot be found: 0
java.lang.UnsupportedOperationException: 35
java.lang.RuntimeException: 1
java.lang.IndexOutOfBoundsException: 1
other error: 0
supported to translate to cvc: 37

### running cvc4 on 35 supported files from above:
cvc4 unsupported: 0
cvc4 error: 0
cvc4 unknown: 28
cvc4 sat: 9
cvc4 unsat: 0
cvc4 no status: 0

### Notes
* the smt2 input files all contain 
(assert true)
(check-sat)
(get-model)
* when cvc4 returns "unknown" for check-sat, according to:
https://github.com/cvc5/cvc5/issues/3427
"When CVC4 says "unknown", by the SMT-LIB standard, it is required to response to get-model queries" -- "with the "best" guess so far"
thus all these cvc4 runs return a model, but there it is not known to be a satisfying model
