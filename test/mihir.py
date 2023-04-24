#!/usr/bin/python                                                                            
                                                                                             
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import RemoteController
import time


class MyTopo(Topo):
    def build(self):
        # Add hosts and switches
        h1 = self.addHost( 'h1' )
        h2 = self.addHost( 'h2' )
        h3 = self.addHost( 'h3' )
        s1 = self.addSwitch( 's1' )
        s2 = self.addSwitch( 's2' )
        s3 = self.addSwitch( 's3' )


        # Add links
        self.addLink( h1, s1 )
        self.addLink( s1, s2 )
        self.addLink( h2, s2 )
        self.addLink( s2, s3 )
        self.addLink( h3, s3 )  
        # self.addLink( s3, s1 )


def simpleTest():
    "Create and test a simple network"
    
    topo = MyTopo()
    
    net = Mininet(topo=topo, autoSetMacs=True, controller = lambda name : RemoteController(name,ip='127.0.0.1', port=6633), autoStaticArp=True)
    net.start()

    print( "Dumping host connections" )
    dumpNodeConnections(net.hosts)

    # print( "Testing network connectivity" )
    # net.pingAll()  

    # for host in net.hosts:
        # print(f'{host.name} MAC address: {host.MAC()}')

    # for switch in net.switches:
        # print(f'{switch.name} MAC address: {switch.MAC()}')

    CLI(net)
    net.stop()

    # h1 = net.get('h1')
    # h3 = net.get('h3')

    # Ping h3 from h1 and get the RTT value
    # result = h1.cmd('ping -c1', h3.IP())
    # rtt = result.split('time=')[-1].split(' ')[0]
    # print(f'RTT from h1 to h3: {rtt} ms')    

    # h1 = net.get('h1')
    # h1.cmd('xterm -e python3 -m http.server 80 &')

    # time.sleep(2)

    # h2 = net.get('h2')
    # h2.cmd('xterm -hold -e curl 10.0.0.1 &')
    # time.sleep(2)
    
    # h3 = net.get('h2')
    # h3.cmd('xterm -hold -e curl 10.0.0.1 &')

    # h3 = net.get('h3')
    # start = time.time()
    # h3.cmd('curl 10.0.0.1')
    # end = time.time()
    # elapsed_time = end - start
    # print(f'Time elapsed: {elapsed_time:.2f} seconds')



    
    

if _name_ == '_main_':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()

# the server created on h1 is blocking the client from starting at h2