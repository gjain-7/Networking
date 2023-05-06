import heapq
from typing import *


def cost(bandwidth, delay):
    return delay + 1 / (1 + bandwidth)


def dijkstra(src, bw_query, adj, links):
    # Initialize distances and paths
    distances = {vertex: float("inf") for vertex in adj}
    distances[src] = 0
    paths = {vertex: [] for vertex in adj}
    paths[src] = [src]

    # Initialize heap priority queue
    pq = [(0, src)]

    # Run Dijkstra's algorithm
    while pq:
        (dist, curr_vertex) = heapq.heappop(pq)

        # Skip visited vertices
        if dist > distances[curr_vertex]:
            continue

        # Update distances and paths for neighboring vertices
        for neighbor in adj[curr_vertex]:
            if ((curr_vertex, neighbor) not in links) or (
                links[(curr_vertex, neighbor)][0] < bw_query
            ):
                continue
            weight = cost(*links[(curr_vertex, neighbor)])
            new_dist = dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                paths[neighbor] = paths[curr_vertex] + [neighbor]
                heapq.heappush(pq, (new_dist, neighbor))

    # Return shortest paths and distances
    return distances, paths


def load_data(file, duplicate_entries=True):
    "Stores the link data (bw, delay)"
    with open(file, "r") as f:
        data = {}
        lines = f.read().strip().split("\n")
        lines = [line.split(" ") for line in lines]
        for row in lines:
            node1, node2 = row[0], row[1]
            data[(node1, node2)] = [int(row[2]), int(row[3])]
            if duplicate_entries:
                data[(node2, node1)] = [int(row[2]), int(row[3])]

    return data
