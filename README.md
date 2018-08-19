# Drone Routing

This is an interesting routing problem which I encountered.

## Problem

Construct a search algorithm to find the optimal (shortest time) path for an electric drone through the given network of charging platforms. Different chargers charge the drone at different rates. The drone does not have to fully charge at any visited charging platform, as long as the drone never runs out of charge while in-flight.

The charger network is detailed in the CSV file.

Assumptions:

- The drone has a maximum range of 365 km on a full charge.
- The drone starts out with a full charge.
- All charging platforms charge the drone at a constant rate - the amount by which the drone’s range is
extended is directly proportional to the time it charges at the charger
- The drone travels along great circle routes between chargers.
- The maximum speed at which the drone can travel is 95 km/hr. You can also assume that it accelerates
to this speed instantly.
- The start and destination points are both charging platforms in the network.
- The drone can stop at as many or as few chargers as needed, as long as the drone never runs out of
charge between chargers or charges to more than 100% at any charger.

Now take any two charging platform IDs in the network as an input and return the shortest (time) path between these two chargers. This path would include every charging platform the drone must stop at, and the amount of time it spends charging at this location.

## My Solution

Each charging node in the input graph is replaced with k nodes, where k is
the number of discrete steps of departure charge the drone can have, e.g. 25%, 50%, 100%.
Each edge in the input graph is replaced with k edges, each connecting to one of k discretized
neighbors for each neighboring input node. We preprocess this graph to  prune it, removing
edges which connect nodes beyond the range of the departure charge at the edge's start
node. The result is a solution with optimality bounded by the number of discretization steps.

### Dependencies

- Python 2 or 3
- `pip install pandas numpy geopy networkx`

### Usage

```shell
python route.py <from> <to>
```
