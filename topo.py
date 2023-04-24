from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.util import dumpNodeConnections
from mininet.clean import cleanup


class MyTopo(Topo):
    def build(self):
        # Add hosts
        h1 = self.addHost("h1")
        h2 = self.addHost("h2")

        # Add switches
        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")
        s3 = self.addSwitch("s3")

        # Add links
        self.addLink(h1, s1, bw=10)
        self.addLink(s1, s2, bw=10)
        self.addLink(s2, s3, bw=10)
        self.addLink(h2, s3, bw=10)

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
    cleanup()
    setLogLevel("info")  # Tell mininet to print useful information
    run()
