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
"""

data_file_names = [
    "results/test-2024-06-09-11-37-29-nday-mac-notexclusive-without-power-perturbed.csv",
    "results/test-2024-06-12-11-44-52-tumbo-exclusive.csv",
    "results/test-2024-06-18-10-56-24-tumbo-exclusive.csv"
]
# model,command_number,method,scope,timeout,return_code,time_elapsed,satisfiability
# tuple position for data read from csv
input_model = 0
input_cmdnum = 1   # not used
input_method = 2
input_scope = 3
input_timeout = 4
input_return_code = 5
input_time_elapsed = 6
input_satisfiability = 7

OK_CODE = 0
TIMEOUT_CODE = 999

TIMEOUT_VALUE = 3600

SKIP_FIRST_LINE = True # file has a header line

method1 = 'portus-full'
method2 = 'kodkod'
methods_used_list = [method1, method2]

outlier_threshold = 0.8
show_outliers = True
stop_on_checks = False 

#scatter_plot_file = 'plot'+data_file_name.replace('.csv','.tex')

# -- end configuration ---------------

import csv
import statistics

# one-dimensional dictionary data[model][method] = [return_code, time_elapsed, satisfiability]
data = {}
# position of fields within data 
data_return_code = 0
data_time_elapsed = 1
data_satisfiability = 2

total_models = 0


# read the csv file and create a list of tuples of data
# [ [model, method, time_elapsed, result], ...]
# for return_code ok and non-timeout rows
timeout_old = None
for data_file_name in data_file_names:
    skip_first = SKIP_FIRST_LINE
    with open(data_file_name) as f:
        reader = csv.reader(f,delimiter=",")   
        for row in reader:
            if not(skip_first):
                model = row[input_model].strip()
                method = row[input_method].strip()
                return_code = int(row[input_return_code].strip())
                time_elapsed = float(row[input_time_elapsed].strip())
                satisfiability = row[input_satisfiability].strip()
                timeout = int(row[input_timeout].strip())
                if (return_code != OK_CODE and return_code != TIMEOUT_CODE):
                    print(str(row) +" has non-okay return code")
                else:
                    # sanity check: all timeouts should be the same in one file
                    if (timeout_old == None):
                        # first row of data
                        timeout_old = timeout
                    
                    if (timeout_old != timeout):
                        print("Timeouts not the same on all rows")
                        print(row)
                        exit(1)

                    # sanity check: time is between 0 and timeout
                    if return_code != TIMEOUT_CODE and(time_elapsed < 0 or time_elapsed > TIMEOUT_VALUE ):
                        print("Time recorded is not between 0 and timeout")
                        print(row)
                        exit(1)

                    # sanity check: method used is one we know
                    if not(method in methods_used_list):
                        print(row)
                        print("Unknown method")
                        exit(1)

                    # add the data to the dictionary
                    # for now, ignore timeouts
                    #if (return_code != TIMEOUT_CODE):
                    if not(model in data.keys()):
                        data[model] = {}
                    data[model][method] = [return_code,time_elapsed, satisfiability]
                    #else:
                        #print("Ignored: "+model+" because it timeout out for "+method)

            else:
                skip_first = False




    # check we have results for the every method for every model or else get rid of model
    # remove models that we don't have data for all methods
    # have to get list of keys first because removing from dictionary during loop
    keys = list(data.keys())
    for mod in keys:
        for meth in methods_used_list:
            if not(meth in data[mod].keys()):
                print("All methods did not complete on model "+mod)
                del data[mod]
                break

    print("# models with results for all methods "+str(len(data.keys())))

    # count SAT/UNSAT and make sure they agree
    sat = 0
    unsat = 0
    flag = False
    for mod in data.keys():
        x = None
        for meth in methods_used_list:
            #print(mod)
            #print(meth)
            if data[mod][meth][data_return_code] != TIMEOUT_CODE:
                if (x is None):
                    x = data[mod][meth][data_satisfiability]
                    # count the first one
                    if x == "SAT":
                        sat += 1
                    elif x == "UNSAT":
                        unsat += 1
                    else:
                        print("Unknown result: "+ mod + " "+ method)
                        exit(1)
                elif (x != data[mod][meth][data_satisfiability]):
                    print("Sat/unsat result does not agree "+mod)
                    flag = True
                else:
                    # results agree 
                    pass

    if stop_on_checks and flag:
        exit(1)

    print("# SAT: "+str(sat))
    print("# UNSAT: "+ str(unsat))

    ratio = {}
    actual_portus_time = {}
    print("model, ratio of "+method1 +" over "+method2)
    for mod in data.keys():
        if data[mod][method1][data_return_code] != TIMEOUT_CODE and data[mod][method2][data_return_code] != TIMEOUT_CODE:
            ratio[mod] = (data[mod][method1][data_time_elapsed] / data[mod][method2][data_time_elapsed]) *100            
        else:
            ratio[mod] = TIMEOUT_CODE
        actual_portus_time[mod] = data[mod][method1][data_time_elapsed]


    f = open(data_file_name.replace('.csv','.stats'),'w')
    for mod in data.keys():
        f.write(mod[len("expert-models/"):]+ ", " +str(round(actual_portus_time[mod],2)) + ", " + str(round(ratio[mod],2)) + "%" + ", " + data[mod][method1][data_satisfiability] +"\n")
    f.close()

exit(1) # ---------------

# possible methods
methods_total_time = {}
methods_total_models = {}

for m in methods_used_list:
    methods_total_time[m] = 0
    methods_total_models[m] = 0


total_models = len(data.keys())
print("Num models with data for all methods: " + str(total_models))

for m in methods_used_list:
    methods_total_time[m] = 0

for mod in data.keys():
    for meth in methods_used_list:
        methods_total_time[m] += data[mod][meth][data_time_elapsed]

for m in methods_used_list:
    print("Total time for "+m+"  "+str(round(methods_total_time[m],2)))

print("total"+method1+"/total"+method2+" "+str(round(methods_total_time[method1]/methods_total_time[method2],2)))

num_method1_faster = 0
num_method2_faster = 0
num_same = 0
max_time = 0
ratio_data = []
for mod in data.keys():
    m1_time = data[mod][method1][data_time_elapsed]
    m2_time = data[mod][method2][data_time_elapsed]
    if m1_time > max_time:
        max_time = m1_time
    if m2_time > max_time:
        max_time = m2_time
    if m1_time > m2_time:
        num_method1_faster += 1
    elif m1_time < m2_time:
        num_method2faster += 1
    else:
        num_same = +1
    ratio = m1_time / m2_time
    ratio_data.append(ratio)
    # find outliers
    if ratio < outlier_threshold and show_outliers:
        print("Outlier: "+ mod)
        print(method1 +" time:"+str(round(m1_time,2)) )
        print(method2 +" time:"+str(round(m2_time,2)) +"\n")


print("Number of files "+method1+" faster "+str(num_method1_faster))
print("Number of files "+method2+" faster "+str(num_method2_faster))
print("Number of files with same time for both methods" + str(num_same))


print("Geometric Mean: "+str(round(statistics.geometric_mean(ratio_data),2)))
print("Median: "+str(round(statistics.median(ratio_data),2)))
print("Min: "+str(round(min(ratio_data),2)))
print("Max: "+str(round(max(ratio_data),2)))
print("Std deviation: "+str(round(statistics.stdev(ratio_data),2)))

# stuff for creating a scatterplot

# The next two functions are used when we want to
# see the plot by itself in a file
def plot_start_file():
    '''
    \\documentclass[11pt]{article}
    \\usepackage{tikz}
    \\usepackage{pgfplots}
    \\pgfplotsset{width=7.5cm,compat=1.12}
    \\usepgfplotslibrary{fillbetween}
    \\begin{document}
    '''

def plot_end_file():
    '''
    \\end{document}
    '''

def plot_start(plotf,xname,yname,xmax,ymax):
    plotf.write('''
    % This file is auto-generated by tally-results.py

    \\begin{tikzpicture}
    \\pgfplotsset{
       scale only axis,
    }

    \\begin{axis}[
      axis lines = middle,
      xmin=0,
      ymin=0,
      xmax='''+str(xmax)+''',
      ymax='''+str(ymax)+''',
      x label style={at={(axis description cs:0.5,-0.1)},anchor=north},
      y label style={at={(axis description cs:-0.11,.5)},rotate=90,anchor=south},
      xlabel=
    '''+xname+''',
      ylabel=
    '''+yname+''',
    ]
    \\addplot[only marks, mark=x]
    coordinates{ % plot 1 data set
    ''')

def plot_end(plotf):
    plotf.write('''
    }; \\label{plot_one}
    \\draw [blue,dashed] (rel axis cs:0,0) -- (rel axis cs:1,1);
    % plot 1 legend entry
    \\addlegendimage{/pgfplots/refstyle=plot_one}
    \\end{axis}
    \\end{tikzpicture}
    ''')
    

# args are: name of output file, two dictionaries
def make_scatterplot(a,b,g):
    global maxtime
    plotf = open(scatter_plot_file,"w")
    plot_start(plotf,method1+ " (seconds)",method2+ " (seconds)",max_time, max_time)
    av = getv(a)
    bv = getv(b)
    for m in data.keys():
        plotf.write("("+str(data[m][method1])+","+str(data[m][method2])+")\n")
    plot_end(plotf)
    plotf.close()

make_scatterplot(method1, method2)
