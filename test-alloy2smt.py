#!/usr/local/bin/python3

"""
    This script is our process to test the alloy2smt tool
    presented in:

    A new relational solver for the Alloy Analyzer
    Mudathir Mohamed, Baoluo Meng, Andrew Reynolds and Cesare Tinelli
    https://homepage.divms.uiowa.edu/~mahgoubyahia/pdf/crs.pdf
    witg repo: https://github.com/CVC4/org.Alloytools.Alloy

    Set up before running this script:
    
    1) install cvc4 (code does not work with CVC5, which uses different names for CVC4 native input language (https://cvc4.github.io/cvc4-native-input-language.html)
        set cvc4 variable below to its executable

    2) build alloy2smt tool:
        wget https://github.com/CVC4/org.alloytools.alloy/archive/refs/tags/v5.0.0.5.tar.gz (this release is from Sep 23, 2019)
        gunzip v5.0.0.5.tar.gz
        tar -xf v5.0.0.5.tar
        cd org.alloytools.alloy-5.0.0.5/alloy2smt/
        jenv local 11.0
        jenv enable-plugin export (to make sure JAVA_HOME set correctly)

        Fix tool to read use CompUtil.parseEverything_fromFile correctly so it
           can read non-util files imported properly
        on mac:
          sed -i "" 's|Utils.translate(alloy, |Utils.translateFromFile(inputFile, |'  src/main/java/edu/uiowa/alloy2smt/Main.java
        on linux:
          sed -i 's|Utils.translate(alloy, |Utils.translateFromFile(inputFile, |'  src/main/java/edu/uiowa/alloy2smt/Main.java

        chmod +x ./gradlew
        ./gradlew build

    3) set up portus-evaluation Benchmark set 
        git clone https://github.com/WatForm/portus-evaluation.git (which this python script is within)
        make alloy2smt (sets up expert-models, converts to Alloy 6)
        wc -l models-supported.txt (to make sure 74 models)

    4) set 'alloy2smt' variable to 'java -jar ../org.alloytools.alloy-5.0.0.5/alloy2smt/build/libs/alloy2smt_with_dependencies.jar -i '  (".." assumes this script is in a sister directory)

    5) run this script (python3 test-alloy2smt.py)
        this will take while, but outputs stats to stdout
        and all cvc4 output to test-alloy2smt-output-log.txt

    6) Our summary of the results is found in test-alloy2smt-results.md
"""


import subprocess

# overwrite any existing file
models = open("models-supported.txt","r")

alloy2smt = "java -jar ../org.alloytools.alloy-5.0.0.5/alloy2smt/build/libs/alloy2smt_with_dependencies.jar -o tmp.smt2 -i "
cvc4 = "cvc4 "
output_log = "test-alloy2smt-output-log.txt"

# results from alloy2smt generation of .smt2 file
file_cannot_be_found = 0
not_found = []
unsupported = 0 
supported = 0
total = 0
java_runtime_exception = 0
java_indexoutofbounds_exception = 0
other_err = 0 

# results from cvc4
cvc4_unknown = 0
cvc4_sat = 0
cvc4_unsat = 0
cvc4_file_error = 0
cvc4_total_queries_run = 0

outf = open(output_log, "w")

for line in models:
    total += 1
    with subprocess.Popen(alloy2smt+line.strip(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,shell=True) as p:
        # output is the output stream from calling george on the file
        (output, err) = p.communicate()
        if 'File cannot be found.' in err:
            file_cannot_be_found += 1
            not_found.append(line)
        elif 'java.lang.UnsupportedOperationException' in err:
            unsupported += 1
        elif 'java.lang.RuntimeException' in err:
            java_runtime_exception += 1
        elif 'java.lang.IndexOutOfBoundsException' in err:
            java_indexoutofbounds_exception += 1
        elif err:
            other_err += 1
        else:
            supported += 1

            # write smt2 to a temp file and provide as command-line input

            # cvc4 installed on brew won't work on x86_64
            # so have to run on a different machine (tumbo)

            # count the number of queries in the file
            smt2file = open("tmp.smt2", "r")
            lines = '\n'.join(smt2file.readlines())
            num_queries = lines.count('check-sat')
            if (num_queries == 0):
                print("PROBLEM: file contains no queries")
            smt2file.close()

            with subprocess.Popen(cvc4 +' tmp.smt2', stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,shell=True) as q:
                
                print("Running cvc4 on {} queries in {}".format(num_queries,line.strip()))
                # run cvc4 on the file
                # and dump output to log file
                (output, err) = q.communicate()
                outf.write('-----\n')
                outf.write(line.strip()+"\n\n")
                outf.write(output)
                outf.write('\nstderr -----\n')
                outf.write(err)
                outf.write('-----\n')
                outf.flush()
                
                unknown = output.count('unknown')
                unsat = output.count('unsat')
                # this is tricky because "sat" is contained within "unsat" and check-sat
                # 'check-sat' sometimes appears in the output 
                checksat = output.count('check-sat')
                sat = output.count('sat') - unsat - checksat

                if unknown + sat + unsat != num_queries:
                    print("PROBLEM: not finding result for all queries - discarding file")
                    cvc4_file_error += 1
                    # these were all checked by hand to make sure there was an error in CVC4
                    # for these files
                else: 
                    cvc4_total_queries_run += num_queries
                    if unknown > 0:
                        cvc4_unknown += unknown
                    if sat > 0:
                        cvc4_sat += sat
                    if unsat > 0:
                        cvc4_unsat += unsat

print("\nSummary\n")

print("total files: "+str(total))  

print("file cannot be found: "+str(file_cannot_be_found))
for i in not_found:
    print(i)

print("java.lang.UnsupportedOperationException: "+str(unsupported))
print("java.lang.RuntimeException: "+str(java_runtime_exception))
print("java.lang.IndexOutOfBoundsException: "+ str(java_indexoutofbounds_exception))
print("other error: "+str(other_err))
print("supported to translate to cvc: "+str(supported))


print('cvc4 file error: '+str(cvc4_file_error))

print('cvc4 unknown: '+str(cvc4_unknown))
print('cvc4 sat: '+str(cvc4_sat))
print('cvc4 unsat: '+str(cvc4_unsat))

print('cvc4 total queries run: ' + str(cvc4_total_queries_run))

models.close()
outf.close()

