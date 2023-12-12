import argparse
import itertools
import pandas as pd
from pathlib import Path

parser = argparse.ArgumentParser(description='Create tables from a list of output CSV files.')
parser.add_argument('--graphs', nargs='+', help='list of graphs to analyse')
parser.add_argument('--delta', nargs='+', help='simulated annealing delta')
parser.add_argument('--annealing-policy', nargs='+', help='annealing selection policy')
parser.add_argument('--node-policy', nargs='+', default=['HYBRID'], help='node selection policy')
parser.add_argument('--delta-decay', nargs='+', default=[0.0], help='decay rate for delta parameter')
parser.add_argument('--restart-temp', action='store_true', default=False, help='restart temperature')

args = parser.parse_args()
restart_temp = str(args.restart_temp).lower()
print(args)

output_dir = Path('output')
results = []

for graph, annealing_policy, node_policy, delta, delta_decay in itertools.product(args.graphs, args.annealing_policy,
                                                                          args.node_policy, args.delta, args.delta_decay):
    # find and read the CSV file from the output directory
    csv_file = next(output_dir.glob(f'{graph}.graph_AP_{annealing_policy}_NS_{node_policy}'
                                    f'*_D_{delta}*_RT_{restart_temp}_DD_{delta_decay}*.txt'), None)
    if csv_file is None: continue
    output_df = pd.read_csv(csv_file, engine='python', comment='#', sep='\t\t')

    # take the last solution with the best edge cut
    edge_cut = output_df['Edge-Cut']
    best_solution = output_df[edge_cut == edge_cut.min()].iloc[-1]

    results.append({
        'Graph': graph,
        'Annealing': annealing_policy,
        'Node Policy': node_policy,
        'Delta': delta,
        'Delta Decay': delta_decay,
        'Edge-cut': int(best_solution['Edge-Cut']),
        'Swaps': int(best_solution['Swaps']),
        'Migrations': int(best_solution['Migrations'])
    })

results_df = pd.DataFrame(results)
# remove columns which contain only one possible value
if len(args.annealing_policy) == 1:
    del results_df['Annealing']
if len(args.node_policy) == 1:
    del results_df['Node Policy']
if len(args.delta) == 1:
    del results_df['Delta']
if len(args.delta_decay) == 1:
    del results_df['Delta Decay']

print(results_df.to_latex(index=False))