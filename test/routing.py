from utils import dijkstra, get_output

with open("sample2.txt", "r") as f:
    data = f.read().strip()

mylist = data.split("\n")
mylist = [list(map(int, x.strip().split(" "))) for x in mylist]
src, dst, bw_query = mylist[0]
n_host, n_switch = mylist[1]
[n_switch_link] = mylist[2]

src += n_switch
dst += n_switch

switch_links = mylist[3 : 3 + n_switch_link]
host_links = mylist[-n_host:]
adj = {}
links = {}

for link in switch_links:
    s1, p1, s2, p2, bw, delay = link
    cost = delay - bw
    links[(s1, s2)] = [p1, p2, bw, delay, cost]
    links[(s2, s1)] = [p2, p1, bw, delay, cost]

    if s1 not in adj:
        adj[s1] = []
    if s2 not in adj:
        adj[s2] = []
    adj[s1].append(s2)
    adj[s2].append(s1)

for link in host_links:
    h1, s2, p2 = link
    s1 = h1 + n_switch
    bw, delay, cost = 1000000000, 0, 0
    links[(s1, s2)] = [1, p2, bw, delay, cost]
    links[(s2, s1)] = [p2, 1, bw, delay, cost]
    if s1 not in adj:
        adj[s1] = []
    if s2 not in adj:
        adj[s2] = []
    adj[s1].append(s2)
    adj[s2].append(s1)

distances, path = dijkstra(src, bw_query, adj, links)

dst_path = path[dst]

rules = get_output(dst_path, links)

print(dst_path)
print(rules)

output_format = {
    (1, 2): [(1, 1, 2), (2, 1, 2)],
    (1, 3): [(1, 1, 2), (2, 1, 3), (3, 1, 2)],
    (2, 3): [(2, 2, 3), (3, 1, 2)],
    (2, 1): [(2, 2, 1), (1, 2, 1)],
    (3, 1): [(3, 2, 1), (2, 3, 1), (1, 2, 1)],
    (3, 2): [(3, 2, 1), (2, 3, 2)],
}
