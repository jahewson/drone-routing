from __future__ import print_function
import sys

import pandas as pd
import networkx as nx
import numpy as np
from geopy.distance import great_circle


MAX_CHARGE_RANGE = 365 # km
SPEED = 95 # km/h

# 1) build the discretized graph, this is slow, but only needs to happen once

# load data
data = pd.read_csv('charger_locations.csv', index_col=0)

# discretize charge from 5% to 100% in 20 steps, gives 5860 nodes and 903220 feasible edges
charge_percentages = np.linspace(5, 100, num=20, dtype=np.int8)

# returns a given discretized label of an input node
def node_id(id, percent_charge):
    return str(id) + '_' + str(percent_charge)
    
# returns all discretized labels of an input node
def node_ids(id):
    return [node_id(id, p) for p in charge_percentages]

# first add nodes
G = nx.DiGraph()
for row in data.itertuples():
    # generate a node for each discretized departure charge
    for charge_percent in charge_percentages:
        charge_ratio = charge_percent / 100.0
        G.add_node(node_id(row.Index, charge_percent), id=row.Index,
                  departure_charge=charge_ratio,
                  charge_time=charge_ratio * MAX_CHARGE_RANGE / row.chargeRate)

# now add edges, weighted by travel time
for row1 in data.itertuples():
    for row2 in data.itertuples():
        if row1 != row2:
            coord1 = (row1.latitude, row1.longitude)
            coord2 = (row2.latitude, row2.longitude)
            dist = great_circle(coord1, coord2).km
            # only edges within range of a full charge are feasible
            if dist <= MAX_CHARGE_RANGE:
                for src_id in node_ids(row1.Index):
                    src = G.node[src_id]
                    # only edges within range of this specific charge level are feasible
                    charge_range = MAX_CHARGE_RANGE * src['departure_charge']
                    if dist < charge_range:
                        flight_time = dist / SPEED
                        charge_time = src['charge_time']
                        total_time = charge_time + flight_time
                        # add a directed edge to each discretized node for this destination
                        for dest_id in node_ids(row2.Index):
                            dest = G.node[dest_id]
                            G.add_edge(src_id, dest_id, weight=total_time)

# 2) find the shortest path

src = int(sys.argv[1])
dst = int(sys.argv[2])
try:
    # 100% charge at start node
    # 100% charge at end node, becuase it is guaranteed to exist and all end nodes have zero cost
    path = nx.dijkstra_path(G, node_id(src, 100), node_id(dst, 100))
except nx.NetworkXNoPath:
    print('No possible path')
    sys.exit(1)

# TODO: We could compute this path's optimal charging times by postprocessing it: ignoring
# discretization, setting all charging times to zero and walking the path, taking any necessary
# charge from the fastest non-fully-utilized prior charger.

# 3) print the solution

# start
res = [G.nodes[path[0]]['id']]
# charging stops
for i in range(len(path) - 2):
    dest = G.nodes[ path[i + 1]]
    res.append(dest['id'])
    res.append(round(dest['charge_time'], 2))
# end
res.append(G.nodes[path[-1]]['id'])

print(', '.join([str(val) for val in res]))
