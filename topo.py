from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.util import dumpNodeConnections
from mininet.clean import cleanup
import utils


class MyTopo(Topo):
    def build(self):
        links = utils.load_data("topology.txt", duplicate_entries=False)
        for link in links:
            nodes = [None] * 2
            for i in range(2):
                if link[i][0] == "h":
                    nodes[i] = self.addHost(link[i])
                else:
                    nodes[i] = self.addSwitch(link[i])

            self.addLink(nodes[0], nodes[1], bw=links[link][0], delay=links[link][1])

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

    for host in net.hosts:
        for intf in host.intfList():
            print(f"{intf.name} MAC address: {intf.MAC()} IP address: {intf.IP()}")
    print()
    for switch in net.switches:
        for intf in switch.intfList():
            if intf.MAC() is not None:
                print(f"{intf.name} MAC address: {intf.MAC()}")

    CLI(net)
    net.stop()

if __name__ == "__main__":
    cleanup()
    setLogLevel("info")  # Tell mininet to print useful information
    run()
    cleanup()
