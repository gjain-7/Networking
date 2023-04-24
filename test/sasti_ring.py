from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.util import dumpNodeConnections
from mininet.clean import cleanup
from controller import startController


class MyTopo(Topo):
    def build(self):
        ring_size = 4
        switches = []
        for i in range(ring_size):
            switches.append(self.addSwitch(f"s{i+1}"))

        for i in range(ring_size):
            self.addLink(switches[i], switches[(i + 1) % ring_size])

        for i in range(0, ring_size, 2):
            self.addLink(switches[i], self.addHost(f"h{i+1}"))

    def main():
        pass


def run():
    topo = MyTopo()

    net = Mininet(
        topo=topo,
        autoSetMacs=True,
        controller=lambda name: RemoteController(name, ip="127.0.0.1", port=6633),
        autoStaticArp=True,
    )
    net.start()

    print("Dumping host connections")
    dumpNodeConnections(net.hosts)

    # print( "Testing network connectivity" )
    # net.pingAll()

    for host in net.hosts:
        print()
        for intf in host.intfList():
            print(f"{intf.name} MAC address: {intf.MAC()}")
        # print(f'{host.name} MAC address: {host.MAC()}')
    for switch in net.switches:
        print()
        for intf in switch.intfList():
            print(f"{intf.name} MAC address: {intf.MAC()}")

    # CLI(net)
    # net.stop()

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


if __name__ == "__main__":
    startController()
    cleanup()
    setLogLevel("info")  # Tell mininet to print useful information
    run()
