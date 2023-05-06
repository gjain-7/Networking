A Ryu based SDN (Software defined Networking) controller to implement switch circuiting using SPF (Shortest Path First) algorithm.

## Description

1. Write a program to discover the topology, including the switches and hosts in the network.
2. Run a client-server program at a pair of hosts to identify the link cost based on the time it takes to traverse the link. You must show all the links in the network and their associated cost. In following format:  
   `<nodei-nodej>: <cost>`  
   For example link between node s3 and s4 has cost 40 than it will be displayed as:  
   `S3-S4: 40`
3. Use the above information for computing the paths in the network for all pairs of hosts in the network. Ask from the user to select a host from where paths to all other hosts need to be computed. Paths will be displayed as following:  
    `Hi-Hj :Hi->Si->Sj->….->Hj`  
    Paths for all pairs of hosts from the selected host must be displayed.
4. Take user input to request the connection by asking for following:
    1. Source and destination host
    2. Service requests are either IPv4 or MAC based
    3. Bandwidth of the service (1-5Mb).  
    
    Identify the switches where configuration need to be updated. Provide details of the configuration to be written over each intermediate switch on the path.

5. Include the already configured services in path computation. Here you need to keep track of the available bandwidth of the link (how much utilized, how much unutilized). Based on the delay and available bandwidth information compute the new cost for the link. Cost will be updated with changes in the available bandwidth.


### Built With

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.
* [Mininet](mininet.org)
* [Ryu SDN Framework](ryu-sdn.org)


## Getting Started

To get a local copy up and running follow these simple example steps.


### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
- #### Python 3.9  
  _This only works on python3.9 since `ryu` no longer maintained._
- #### Mininet  
  follow installation guide [here](http://mininet.org/download/).
- #### Ryu
  ```sh
  pip install ryu
  ```


### Installation

1. Install dependencies
   ```sh
   pip install -r requirements.txt
   ```
   _Note : Make sure to keep the `eventlet` (pip package) version @0.30.2 (already there in requirements)_
2. Enter the your topology in the `topology.txt`.

    Format for the topology:
    - Each line contains the entry in the form 
        ```txt
        <node1> <node2> <bandwidth> <delay>
        ```
    - `<node>` can be of form `s<switch-number>` or `h<host-number>`
    - Switch and Host numbering need to begin from 1 and cannot a skip any integer in between. 
        ```txt
        h1 s1 
        h2 s1
        h4 s1
        ```
        For example, the above topology is invalid because `h3` is missing.
3. You may modify your cost function in `utils.cost`


### Usage

1. Start the controller
    ```sh
    python controller.py
    ```
2. Start mininet
    ```sh
    sudo python3 topo.py
    ```
3. Start the client
    ```sh
    python client.py
    ```


## Acknowledgments

This project was done as a part of course project for _CS 306 - Computer Networking_ course.