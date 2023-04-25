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


def get_output(dst_path, links):
    rules = {(dst_path[0], dst_path[-1]): []}
    ports = []
    for i in range(len(dst_path) - 1):
        s1, s2 = dst_path[i], dst_path[i + 1]
        ports.append(links[(s1, s2)][0])
        ports.append(links[(s1, s2)][1])
    ports = ports[1:-1]
    cnt = 0
    for i in range(len(dst_path) - 2):
        s = dst_path[i + 1]
        port1 = ports[cnt]
        port2 = ports[cnt + 1]
        cnt += 2
        rules[(dst_path[0], dst_path[-1])].append((s, port1, port2))
    print(ports)
    return rules


def load_data(file, duplicate_entries=True):
    "Stores the link data (bw, delay)"
    with open(file, "r") as f:
        data = {}
        lines = f.read().strip().split("\n")
        lines = [line.split(" ") for line in lines]
        for row in lines:
            node1, node2 = row[0], row[1]
            data[(node1, node2)] = [int(row[2]), int(row[3])]
            if(duplicate_entries):
                data[(node2, node1)] = [int(row[2]), int(row[3])]

    return data
