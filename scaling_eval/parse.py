import csv
from collections import defaultdict


def parse_results(results_path, old_style=False):
    results = defaultdict(list)
    with open(results_path, "r") as csv_file:
        reader = csv.reader(csv_file)
        next(reader) # skip header
        if old_style:
            for model, command, sig, scope, portus, kodkod in reader:
                results[(model, int(command), int(sig))].append({
                    "scope": int(scope),
                    "portus": float(portus) if portus != "timeout" else portus,
                    "kodkod": float(kodkod) if kodkod != "timeout" else kodkod,
                })
        else:
            for (
                model,
                command,
                sig,
                scope,
                correctness,
                portus_timeout,
                portus_sat_result,
                portus_retcode,
                portus_stats_ok,
                portus_wc_time_s,
                portus_user_time_s,
                portus_sys_time_s,
                portus_cpu_time_s,
                portus_peak_rss_kb,
                portus_avg_rss_kb,
                portus_avg_total_mem_kb,
                portus_num_page_faults,
                portus_num_minor_page_faults,
                kodkod_timeout,
                kodkod_sat_result,
                kodkod_retcode,
                kodkod_stats_ok,
                kodkod_wc_time_s,
                kodkod_user_time_s,
                kodkod_sys_time_s,
                kodkod_cpu_time_s,
                kodkod_peak_rss_kb,
                kodkod_avg_rss_kb,
                kodkod_avg_total_mem_kb,
                kodkod_num_page_faults,
                kodkod_num_minor_page_faults,
            ) in reader:
                if correctness != "True" and not (portus_sat_result == "UNSURE" or kodkod_sat_result == "UNSURE"):
                    print(f"WARNING: {model} cmd {command} sig {sig} scope {scope} is incorrect!")
                results[(model, int(command), int(sig))].append({
                    "scope": int(scope),
                    "portus": float(portus_cpu_time_s) if portus_timeout != "True" else "timeout",
                    "kodkod": float(kodkod_cpu_time_s) if kodkod_timeout != "True" else "timeout",
                })
    return results
