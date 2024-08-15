#!venv/bin/python3

"""
    This script is for tallying results (totals, comparisons) for use in a paper from a .csv file
    
    To do:
    - divide results by sat and unsat if there are enough of each
    - how to deal with timeouts?
    - averaging over multiple reps of run

    - scope of -1 means default command scopes
    result codes:
    0 means okay
    -1 means timeout
    1 means some other problem

  We can get UNKNOWN result but not a timeout ...

"""

data_file_name ="results/2024-08-13-20-22-15-datatypes-evaluate-z3-60min-tumbo-results-no-ertms.csv"

expected_number_of_iterations = 3

# tuple position for input data read from csv
# skipping some unneeded fields since we are just
# looking at fortress options right now

# for the input
def i_model(x):
    return x[0].strip()
def i_compiler(x):
    return x[2].strip()
def i_solver(x):
    return x[5].strip()
def i_timeout(x):
    return float(x[6].strip())
def i_return_code(x):
    return x[7].strip()
def i_time_elapsed(x):
    return float(x[8])
def i_satisfiability(x):
    return x[9].strip()

OK_CODE = 0
TIMEOUT_CODE = 999


SKIP_FIRST_LINE = True # file has a header line

compiler_options = [ 
    "Standard",
    "DatatypeWithRangeEUF",
    "DatatypeNoRangeEUF",
    "Evaluate",
    "EvaluateQDef",
]
solver_options = [
    "Z3NonIncCli"
]
# -- end configuration ---------------

import csv
import statistics

# for the internal data
def d_model(x):
    return x[0].strip()
def d_compiler(x):
    return x[1].strip()
def d_solver(x):
    return x[2].strip()
def d_return_code(x):
    return x[3].strip()
def d_time_elapsed(x):
    return float(x[4])
def d_satisfiability(x):
    return x[5].strip()

unknown_satisfiability = "UNKNOWN"
unsure_satisfiability = "UNSURE"
unknown_time = -1
unknown_return_code = 999

data_input = []
print("---- " + data_file_name)
skip_first = SKIP_FIRST_LINE
timeout_old = None
with open(data_file_name) as f:
    reader = csv.reader(f,delimiter=",")   
    for row in reader:
        if not(skip_first):
            if row!=[]:
                data_input.append(row)
        skip_first = False
# will be the same timeout for the whole file
timeout = i_timeout(data_input[0])

# Get the models
all_models = set(map(lambda x: i_model(x), data_input))

# create data that is the average of the times for the three iterations
# of each model, compiler, solver combo
data = []
for mod in all_models:
    for comp in compiler_options:
        for solv in solver_options:
            ll = list(filter(lambda x: i_model(x)==mod and 
                                       i_compiler(x)==comp and 
                                       i_solver(x)==solv,data_input))
            if len(ll)!=0 and i_satisfiability(ll[0])!=unknown_satisfiability and len(ll)!=expected_number_of_iterations:
                print("Incorrect number of iterations for "+mod+" "+comp+" "+solv)
                exit(1)
            sum = 0
            rc = i_return_code(ll[0])
            status = i_satisfiability(ll[0])
            for x in ll:
                unk = False 
                if i_return_code(x) != rc:
                    print("Different result codes "+mod)
                    exit(1)
                if i_satisfiability(x) != status:
                    print("Different satisfiability "+mod)
                    exit(1)
                if i_time_elapsed(x)!=unknown_time:
                    sum += i_time_elapsed(x)
                else:
                    unk = True 
            if not(unk):
                data.append([mod,comp,solv,rc,str(sum/expected_number_of_iterations),status])
            else:
                # could be one unknown in iterations or all unknown
                if sum != 0:
                    print("Some unknown results and some timed results for "+mod)
                    exit(1)
                else:
                    # all unknown
                    data.append([mod,comp,solv,rc,unknown_time,status])


# now we work with data that has only one entry per model
# for each compiler/solver combo, count how many timeouts
print("Unknowns (includes timeouts)")
for comp in compiler_options:
    for solv in solver_options:
        ll = list(filter(lambda x: d_compiler(x)==comp and 
                                   d_solver(x) ==solv and 
                                   d_satisfiability(x)==unknown_satisfiability, data))
        print(comp+", " + solv + " " + str(len(ll)))

# all the models,comp that Z3 got UNKNOWN on, CVC5 also did, CVC5 got unknown on two others     



# this works because unknown_time is -1
# and there will be no times between -1 and 0
ranges = [unknown_time, 5,10,15,30,60,timeout]

winners = {}
count = {}
for comp in compiler_options:
    winners[comp] = {}
    count[comp] = {}
    for solv in solver_options:
        winners[comp][solv] = 0
        count[comp][solv] = {}
        for r in ranges:
            count[comp][solv][r] = 0

for a in all_models:
    model_data = list(filter(lambda x:d_model(x) == a and 
                                      d_satisfiability(x)!=unknown_satisfiability,data))
    if model_data != []:
        model_data.sort(key=lambda x:d_time_elapsed(x))
        winners[d_compiler(model_data[0])][d_solver(model_data[0])] += 1
    else:
        print("All unknown for: "+a)

print("\n")
print("Tally winners on models")
for comp in compiler_options:
    for solv in solver_options:
        print(comp + ", " + solv + " " + str(winners[comp][solv]))



for r in range(0,len(ranges)):
    if r == 0:
        xx = list(filter(lambda x:d_time_elapsed(x) <= ranges[r],data))
    else:
        xx = list(filter(lambda x:ranges[r-1] < d_time_elapsed(x) and d_time_elapsed(x) <= ranges[r],data))
    for comp in compiler_options:
        for solv in solver_options:
            # we can have some that take a limited time but 
            # are unknown satisfiability
            # we want to count those as unknown_time
            yy = list(filter(lambda x:d_compiler(x) == comp and d_solver(x) == solv and d_satisfiability(x)!=unsure_satisfiability,xx))
            yy_unsure_time = list(filter(lambda x:d_compiler(x) == comp and d_solver(x) == solv and d_satisfiability(x)==unsure_satisfiability,xx))
            count[comp][solv][ranges[r]] += len(yy)
            count[comp][solv][unknown_time] += len(yy_unsure_time)


print("\nCounts in ranges\n")
print("comp+solv, ",end="")
for x in ranges[1:]:
    print("<="+str(x)+", ",end="")
print("TIMEOUT")
for c in compiler_options:
    for s in solver_options:
        print(c +" + "+s+", ",end="")
        for r in ranges[1:]:
            print(str(count[c][s][r])+", ",end="")
        # timeout printed last
        print(str(count[c][s][unknown_time]))


