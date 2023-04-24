# http://10.250.11.109:8080/hosts
import requests
from ast import literal_eval
import json
from utils import cost

# from utils import cost
main_url = "http://10.250.11.109:8080"

# host1:host2: host1->S1->S2->host2
def display_paths(host, data):
    for key, value in data.items():
        if key == host:
            continue
        if key[0] == "h":
            print(f"{host}-{key} :", end="")
            for i in range(len(value) - 1):
                print(f"{value[i]}->", end="")
            print(f"{value[-1]}")
    print()


def pretify(data):
    nodes_done = {}
    # node1-node2 : cost
    for k, v in data.items():
        if nodes_done.get(k[0] + k[1], 0) == 1:
            continue
        print(k[0] + "-" + k[1] + " : " + str(cost(v[0], v[1])))
        nodes_done[k[0] + k[1]] = 1
        nodes_done[k[1] + k[0]] = 1


def add_connection(main_url):
    url = main_url + "/add"
    print("1 MAC Based\n2 IP Based\n")
    n = input("Enter your choice: ")
    data = {"id_spec": "mac" if n == "1" else "ip", "src": "", "dst": "", "bw": 0}
    while 1:
        print("Enter host1 host2 bandwidth")
        inp_str = input()
        inp_list = inp_str.split()
        if len(inp_list) < 3:
            print("Invalid Input...\nTry Again!\n")
            continue
        host1 = inp_list[0]
        host2 = inp_list[1]
        try:
            bw = float(inp_list[2])
        except ValueError:
            print("Invalid Input... Bandwidth must be a number\nTry Again!\n")
            continue
        data["id_spec"] = "gn"
        data["src"] = host1
        data["dst"] = host2
        data["bw"] = bw
        try:
            response = requests.post(url, json=data)
        except:
            print("Connection Refused... Try Again Later!\n")
            exit(0)

        print(response.text)
        res = response.json()
        if len(res) == 0:
            print("No possible path found\n")
        else:
            print(res)
            print()


def get_links(main_url):
    url = main_url + "/links"
    try:
        response = requests.get(url)
        res = response.json()
        data = {literal_eval(k): v for k, v in json.loads(res).items()}
    except requests.exceptions.ConnectionError:
        print("Connection Refused... Try Again Later!\n")
        exit(0)
    pretify(data)


# minimum cost from a particular host to all other hosts
def getMinPath(main_url):
    while 1:
        host = input("Enter host name: ")
        url = f"{main_url}/paths/{host}"
        try:
            response = requests.get(url)

            # res=response.json()
        except requests.exceptions.ConnectionError:
            print("Connection Refused... Try Again Later!\n")
            exit(0)
        res = response.json()
        display_paths(host, res)


def get_rules(main_url):
    switch_num = int(input("Enter switch number: "))
    url = f"{main_url}/flows/{switch_num}"
    try:
        response = requests.get(url)

        # res=response.json()
    except requests.exceptions.ConnectionError:
        print("Connection Refused... Try Again Later!\n")
        exit(0)


# getMinPath(main_url)

add_connection(main_url)


# links=get_links(main_url)
# print(links)

# get_links(main_url)

# get_rules(main_url)
