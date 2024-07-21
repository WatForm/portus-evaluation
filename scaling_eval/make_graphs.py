import argparse
from pathlib import Path

import scipy.optimize
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from scaling_eval.parse import parse_results


FIGS_PATH = "figs"


def affine_exp(x, a, b):
    # fit this function in log-space
    return np.exp(a*x + b)


def expfit(x, y):
    if len(x) <= 2:
        return (np.nan, np.nan), -1
    popt, _ = scipy.optimize.curve_fit(lambda x, *popt: np.log(affine_exp(x, *popt)), x, np.log(y), p0=[0.05, 1], maxfev=50000)
    mse = np.mean((np.log(y) - np.log(affine_exp(x, *popt)))**2)
    return popt, mse


def plot_expfit(min_x, max_x, popt, mse, name, resolution=0.1):
    x = np.arange(min_x, max_x, resolution)
    y = affine_exp(x, *popt)
    plt.plot(x, y, label=f"{name} MSE: {mse:.2f} popt={popt}", linewidth=0.5, linestyle='--')


def plot_result(scopes, portus, kodkod, plot_timeout: bool, title, timeout=60):
    plt.plot(scopes, portus, label="portus")
    plt.plot(scopes, kodkod, label="kodkod")
    if plot_timeout:
        plt.plot(scopes[-1], timeout, "rx", label="timeout")
    plt.title(title)
    plt.legend(loc="upper left")
    plt.xlabel("Scope")
    plt.ylabel("Solving time (s)")
    plt.yscale("log")


def plot_popt_histo(portus_popts, kodkod_popts):
    portus_scaling_factors = np.array([a for a, _ in portus_popts if not np.isnan(a)])
    kodkod_scaling_factors = np.array([a for a, _ in kodkod_popts if not np.isnan(a)])

    portus_minus_kodkod_scaling = portus_scaling_factors - kodkod_scaling_factors
    plt.hist(portus_minus_kodkod_scaling, bins=20)
    plt.title("Portus scaling factor - Kodkod scaling factor")


def make_title_and_path(model_path, command, sig):
    model = Path(model_path).name
    title = f"{model}, cmd {command}, sig {sig}"
    path = Path(FIGS_PATH) / f"{model}-cmd{command}-sig{sig}.png"
    return title, str(path)


def main():
    parser = argparse.ArgumentParser(prog="make_graphs", description="Make graphs from scaling_eval CSV output")
    parser.add_argument("path", help="Path to the results CSV")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout used when running scaling_eval")
    args = parser.parse_args()

    # ensure figs dir exists
    figs_path = Path(FIGS_PATH)
    figs_path.mkdir(parents=True, exist_ok=True)
    print(f"Outputting figures to {figs_path.absolute()}.")

    results = parse_results(args.path)
    print(f"Loaded {len(results)} results.")

    portus_popts = []
    kodkod_popts = []

    for (model, command, sig), result in tqdm(results.items()):
        scopes = np.array([res["scope"] for res in result])
        portus = np.array([res["portus"] if res["portus"] != "timeout" else args.timeout for res in result])
        kodkod = np.array([res["kodkod"] if res["kodkod"] != "timeout" else args.timeout for res in result])
        any_timeout = result[-1]["portus"] == "timeout" or result[-1]["kodkod"] == "timeout"

        portus_popt, portus_mse = expfit(scopes, portus)
        kodkod_popt, kodkod_mse = expfit(scopes, kodkod)
        plot_expfit(scopes.min(), scopes.max(), portus_popt, portus_mse, "Portus")
        plot_expfit(scopes.min(), scopes.max(), kodkod_popt, kodkod_mse, "Kodkod")
        portus_popts.append(portus_popt)
        kodkod_popts.append(kodkod_popt)

        title, path = make_title_and_path(model, command, sig)
        plot_result(scopes, portus, kodkod, any_timeout, title, timeout=args.timeout)

        plt.savefig(path)
        plt.clf()

    plot_popt_histo(portus_popts, kodkod_popts)
    plt.savefig(str(Path(FIGS_PATH) / "scaling-factor-histogram.png"))
    plt.clf()


if __name__ == "__main__":
    main()
