from bbopt import BlackBoxOptimizer
import sys
from argparse import ArgumentParser
import json
from pprint import pprint

def convertToConfig(x):
    type = types[int(round(x[0]))]
    size = sizes[int(round(x[1]))]
    index = int(round(x[2])) % len(configs[size])
    num = configs[size][index]
    return type, size, num

def get_runtime():
    bb.run(alg="gaussian_process")

    # Let's use some parameters!
    x0 = bb.randrange("x0", 0, 2, guess=1)
    x1 = bb.randrange("x1", 0, 2, guess=1)
    x2 = bb.randrange("x2", 0, 9, guess=1)
    x = [x0, x1, x2]
    type, size, num = convertToConfig(x)
    dir = parent_dir + str(num) + '_'+ type+'.'+size+ '_'+ app + "_" +system + "_" + datasize + "_1/"
    jsonName= dir + 'report.json'
    report = json.load(open(jsonName, 'r'))
    runtime = float(report["elapsed_time"])
    bb.remember({"runtime": runtime})
    bb.minimize(runtime)

configs = {
'large': [4, 6, 8, 10, 12, 16, 24, 32, 40, 48],
'xlarge': [4, 6, 8, 10, 12, 16, 20, 24],
'2xlarge': [4, 6, 8, 10, 12]
}
types = ['m4', 'c4', 'r4']
sizes = ['large', 'xlarge', '2xlarge']
parent_dir = '../scout/dataset/osr_multiple_nodes/'

# python plot_all_runtimes.py pagerank spark1.5
# app =sys.argv[1]
# system = sys.argv[2]
app = ''
system=''
datasize = 'huge'

bb = BlackBoxOptimizer(file=__file__)

# Set up command-line interface:
parser = ArgumentParser()
parser.add_argument(
    "-n", "--num-trials",
    metavar="trials",
    type=int,
    default=20,
    help="number of trials to run (defaults to 20)",
)
parser.add_argument(
    "-a", "--application",
    metavar="application",
    type=str,
    default="pagerank",
    help="Name of the application(defaults to pagerank)",
)
parser.add_argument(
    "-s", "--system",
    metavar="system",
    type=str,
    default="spark",
    help="Name of the system (defaults to spark)",
)
if __name__ == "__main__":
    args = parser.parse_args()

    print(args.num_trials)
    app = args.application
    system = args.system
    # Main loop:
    for i in range(args.num_trials):
        get_runtime()
        print("Summary of run {}/{}:".format(i+1, args.num_trials))
        pprint(bb.get_current_run())
        print()

    print("\nSummary of best run:")
    pprint(bb.get_optimal_run())
