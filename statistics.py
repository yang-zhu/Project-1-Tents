import os
from collections import defaultdict
from encoding import Grid, solveGrid
import json
import seaborn as sns
import matplotlib.pyplot as plt
import argparse

def relativePath(*path):
    return os.path.join(os.path.dirname(__file__), *path)

parser = argparse.ArgumentParser()
parser.add_argument('cadical', help='path to CaDiCaL')
args = parser.parse_args()

# Solve puzzles and store the statistics in "statistics.txt". The sizes of the puzzles range from 100*10 to 100*120 with an interval of 10 regarding the width.
# If "statistics.txt" already exists, then read the data from this file instead.
if not os.path.isfile('statistics.txt'):
    stats_dict = defaultdict(list)
    for width in range(10,121,10):
        for i in range(1,11):
            filename = 'tents-100x'+str(width)+'-'+str(i)+'.txt'
            print("solving", filename)
            path = relativePath('puzzles', filename)
            grid = Grid.fromFile(path)
            
            stats1 = solveGrid(args.cadical, grid, tree_without_tent=True, no_binary = True, return_stats = True, timeout = 60)
            stats_dict['Version'].append('v1')
            stats_dict['Variables'].append(stats1['Variables'])
            stats_dict['Clauses'].append(stats1['Clauses'])
            stats_dict['Time'].append(stats1['Solving time'])
            stats_dict['Size'].append(100*width)
            
            stats2 = solveGrid(args.cadical, grid, no_binary = True, return_stats = True, timeout = 60)
            stats_dict['Version'].append('v2')
            stats_dict['Variables'].append(stats2['Variables'])
            stats_dict['Clauses'].append(stats2['Clauses'])
            stats_dict['Time'].append(stats2['Solving time'])
            stats_dict['Size'].append(100*width)
            
            stats3 = solveGrid(args.cadical, grid, return_stats = True, timeout = 60)
            stats_dict['Version'].append('v3')
            stats_dict['Variables'].append(stats3['Variables'])
            stats_dict['Clauses'].append(stats3['Clauses'])
            stats_dict['Time'].append(stats3['Solving time'])
            stats_dict['Size'].append(100*width)

    with open('./statistics.txt', 'w') as f:
        f.write(json.dumps(stats_dict))
else:
    with open('./statistics.txt') as f:
        stats_dict = json.loads(f.read())          

# Display the statistics in three plots. 
fig, axs = plt.subplots(ncols=3)
fig.canvas.set_window_title('Statistics')
plt.subplots_adjust(bottom=0.3, top=0.9)
fig.suptitle('v1: allow trees without tents\nv2: 1:1 mapping between trees and tents\nv3: v2 + count tents using binary addition', ha='left', x=0.1, y=0.15)
for i in range(3):
    axs[i].ticklabel_format(axis='both', style='sci', scilimits=(0,2))   
sns.lineplot(x='Size', y='Variables', hue='Version', data=stats_dict, ax=axs[0])
axs[0].set_title('Number of Variables')
axs[0].set(xlabel = 'number of cells', ylabel = 'variables')
sns.lineplot(x='Size', y='Clauses', hue='Version', data=stats_dict, ax=axs[1])
axs[1].set(xlabel = 'number of cells', ylabel = 'clauses')
axs[1].set_title('Number of Clauses')
sns.lineplot(x='Size', y='Time', hue='Version', data=stats_dict, ax=axs[2])
axs[2].set(xlabel = 'number of cells', ylabel = 'time(s)')
axs[2].set_title('Solving Time')
plt.show()