import requests
from ast import literal_eval
import json
from utils import cost

main_url = "http://10.250.3.163:8080"
# main_url = "http://127.0.0.1:8080"

# host1:host2 :host1->S1->S2->host2
def display_paths(paths):
    for key, value in paths.items():
        if len(value) < 2:
            continue
        if key[0] == "h":
            print(f"{value[0]}-{key} :", end="")
            print("->".join(value))
    print()
    

# in_port,dl_src,dl_dst actions=output
def display_rules(rules):
    for k, v in rules.items():
        print("switch", k)
        for rule in v:
            match = rule["match"]
            action = rule["action"]
            # in_port="s1-eth1",dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:02 actions=output:"s1-eth2"
            print(
                f"""in_port="{k}-eth{match['in_port']}",dl_src={match['src_mac']},dl_dst={match['dst_mac']} actions=output:"{k}-eth{action['out_port']}" """
            )


# <node1-node2> : <cost>
def display_links(links):
    print("\n***************************************\n")
    print("Netwrok Links and Cost\n")
    nodes_done = {}
    for k, v in links.items():
        if nodes_done.get(k[0] + k[1], 0) == 1:
            continue
        print(k[0] + "-" + k[1] + " : " + str(cost(v[0], v[1])))
        nodes_done[k[0] + k[1]] = 1
        nodes_done[k[1] + k[0]] = 1


# Add a new connection between two hosts with a given bandwidth
def add_connection(n):
    url = main_url + "/add"
    print("Enter host1 host2 bandwidth")
    inp_str = input()
    inp_list = inp_str.split()
    if len(inp_list) < 3:
        print("Invalid Input...\nTry Again!\n")
        return
    data = {
        "id_spec": "mac" if n == "1" else "ip" if n == "2" else "",
        "src": "",
        "dst": "",
        "bw": 0,
    }
    host1 = inp_list[0]
    host2 = inp_list[1]
    try:
        bw = float(inp_list[2])
    except ValueError:
        print("Invalid Input... Bandwidth must be a number\nTry Again!\n")
        return
    data["src"] = host1
    data["dst"] = host2
    data["bw"] = bw
    try:
        response = requests.post(url, json=data)
    except:
        print("Connection Refused... Try Again Later!\n")
        exit(0)

    res = response.json()

    print("\nUpdated:\n")
    print("->".join(res["path"]))
    # display_paths(res["path"])
    display_rules(res["rules"])
    print("\nOriginal:\n")
    print("->".join(res["orig_path"]))
    # display_paths(res["orig_path"])
    display_rules(res["orig_rules"])


# Get all links and their costs
def get_links():
    url = main_url + "/links"
    try:
        response = requests.get(url)
        res = response.json()
        data = {literal_eval(k): v for k, v in json.loads(res).items()}
        display_links(data)

    except requests.exceptions.ConnectionError:
        print("Connection Refused... Try Again Later!\n")
        exit(0)
    except Exception as e:
        print(e)
        exit(0)

# Minimum cost from a particular host to all other hosts
def getMinPath():
    host = input("Enter host name: ")
    url = f"{main_url}/paths/{host}"
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        print("Connection Refused... Try Again Later!\n")
        exit(0)
    res = response.json()
    display_paths(res)
        
# Get rules for a particular switch
def get_rules():
    switch_num = int(input("Enter switch number: "))
    url = f"{main_url}/flows/{switch_num}"
    try:
        res = requests.get(url).json()
        print(res)
    except requests.exceptions.ConnectionError:
        print("Connection Refused... Try Again Later!\n")
        exit(0)



def main():
    get_links()
    
    
    while True:
        t=input("\n1 Get rules for a switch\n2 Get minimum path\n3 Add Connections\n4 Exit\nEnter your choice: ")
        if t=='1':
            get_rules()
        elif t=='2':
            while 1:
                getMinPath()
                while 1:
                    choice = input("Do you want to continue(y/n): ")
                    if choice not in ['y','n','Y','N']: print("Invalid Choice!")
                    else: break
                if choice.lower() == 'n':
                    break
        elif t=='3':
                print("\n1 MAC Based\n2 IP Based\n3 Name Based")
                n = input("\nEnter your choice: ")
                while 1:
                    add_connection(n)
                    while 1:
                        choice = input("Do you want to continue(y/n): ")
                        if choice not in ['y','n','Y','N']: print("Invalid Choice!")
                        else: break
                    if choice.lower() == 'n':
                        break
        elif t=='4':
            
            exit(0)
        else:
            print("Invalid Choice\n")



if __name__=='__main__':
    main()