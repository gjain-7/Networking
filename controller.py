from ryu.app.wsgi import WSGIApplication
from ryu.base import app_manager
from ryu.cmd import manager
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls, CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.ofproto import ofproto_v1_3
from ryu.topology import event
from ryu.topology.api import get_host, get_switch, get_link
from rest import RestController
from ryu.lib import dpid, hub


class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {"wsgi": WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.topology_api_app = self
        wsgi = kwargs["wsgi"]
        self.switches = {}
        self.myapp = wsgi
        wsgi.register(RestController, {"controller": self})

        self.lock = hub.Event()
        self.flows = []

        self.rules = {}

        self.hosts = {}
        self.adj, self.link_data = self.load_data("sample.txt")
        # self.ip_to_host = {}
        # self.mac_to_host = {}
        # self.links = {}
        # self.link_ports = {}

    def load_data(self, file):
        "Makes adjacency list and store the link data (bw, delay)"
        with open(file, "r") as f:
            data = {}
            adj = {}
            lines = f.read().strip().split("\n")
            lines = [line.split(" ") for line in lines]
            for row in lines:
                node1, node2 = row[0], row[1]
                data[(node1, node2)] = [int(row[2]), int(row[3])]
                data[(node2, node1)] = [int(row[2]), int(row[3])]
                if node1 not in adj:
                    adj[node1] = []
                if node2 not in adj:
                    adj[node2] = []
                adj[node1].append(node2)
                adj[node2].append(node1)

        return adj, data

    def get_host_by_mac(self, host_mac):
        host_mac = host_mac.replace(":", "")
        return f"h{int(host_mac, 16)}"

    def get_host_by_ip(self, host_ipv4):
        for k, v in self.hosts.items():
            if v.ipv4 and host_ipv4 in v.ipv4:
                return k
        return None
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(
                datapath=datapath,
                buffer_id=buffer_id,
                priority=priority,
                match=match,
                instructions=inst,
            )
        else:
            mod = parser.OFPFlowMod(
                datapath=datapath, priority=priority, match=match, instructions=inst
            )
        datapath.send_msg(mod)

    @set_ev_cls(event.EventHostAdd)
    def host_add_handler(self, ev):
        self.hosts[self.get_host_by_mac(ev.host.mac)] = ev.host
        print(f"added {self.get_host_by_mac(ev.host.mac)}")
        # mac_address = ev.host.mac.replace(":", "")
        # host_id = f"h{int(mac_address, 16)}"

        # print(ev.host.ipv4, ev.host.ipv6)

        # self.mac_to_host[ev.host.mac] = host_id
        # # self.ip_to_host[ev.host.ipv4] = host_id

        # switch_id = f"s{ev.host.port.dpid}"
        # self.link_ports.update({
        #     (switch_id, host_id): (ev.host.port.port_no, 1),
        #     (host_id, switch_id): (1, ev.host.port.port_no)
        # })

    @set_ev_cls(event.EventSwitchEnter)
    def switch_add_handler(self, ev):
        self.switches[ev.switch.dp.id] = ev.switch.dp
        print(f"added s{ev.switch.dp.id}")
        pass
        # links = get_all_link(self.topology_api_app)
        # self.link_ports.update(
        #     {
        #         (link.src.dpid, link.dst.dpid): (link.src.port_no, link.dst.port_no)
        #         for link in links
        #     }
        # )
        # self.link_ports.update(
        #     {
        #         (link.dst.dpid, link.src.dpid): (link.dst.port_no, link.src.port_no)
        #         for link in links
        #     }
        # )

    def add_rule(self, datapath, in_port, src_mac, dst_mac, out_port):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        # Create a match object that matches incoming packets on the specified input port
        match = parser.OFPMatch(in_port=in_port, eth_src=src_mac, eth_dst=dst_mac)
        # Create an action object that sends packets out of the specified output port
        action = parser.OFPActionOutput(out_port)
        # Create a list of instructions that includes the action to take when a packet matches the match criteria
        instructions = [
            parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, [action])
        ]

        # Add the rule to the list of rules for this switch
        if datapath.id not in self.rules.keys():
            self.rules[datapath.id] = []
        obj = {
            "match": {
                "in_port": in_port,
                "src_mac": src_mac,
                "dst_mac": dst_mac,
            },
            "action": {
                "out_port": out_port,
            },
        }
        if obj not in self.rules[datapath.id]:
            self.rules[datapath.id].append(obj)

        # Create a flow mod message that installs the rule on the switch
        flow_mod = parser.OFPFlowMod(
            datapath=datapath,
            match=match,
            instructions=instructions,
            out_port=out_port,
            priority=ofproto.OFP_DEFAULT_PRIORITY,
            idle_timeout=0,
            hard_timeout=0,
            buffer_id=ofproto.OFP_NO_BUFFER,
            out_group=ofproto.OFPG_ANY,
        )

        # Send the flow mod message to the switch
        datapath.send_msg(flow_mod)

    def add_path_rules(self, path):
        rules = {}
        if len(path) < 3:
            print("path too short")
            return rules
        src, dst = self.hosts[path[0]], self.hosts[path[-1]]
        in_port = src.port.port_no
        for i in range(1, len(path) - 2):
            dpid = int(path[i][1:])
            dp = get_switch(self.topology_api_app, dpid)[0].dp
            links = get_link(self.topology_api_app, dpid)
            link = [link for link in links if link.dst.dpid == int(path[i + 1][1:])][0]
            self.add_rule(
                datapath=dp,
                in_port=in_port,
                src_mac=src.mac,
                dst_mac=dst.mac,
                out_port=link.src.port_no,
            )
            rules[path[i]] = self.rules[dpid]
            in_port = link.dst.port_no

        dpid = int(path[-2][1:])
        dp = get_switch(self.topology_api_app, dpid)[0].dp
        self.add_rule(
            datapath=dp,
            in_port=in_port,
            src_mac=src.mac,
            dst_mac=dst.mac,
            out_port=dst.port.port_no,
        )
        rules[path[-2]] = self.rules[dpid]
        return rules

    def send_flow_request(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        req = parser.OFPFlowStatsRequest(
            datapath, 0, ofproto.OFPTT_ALL, ofproto.OFPP_ANY, ofproto.OFPG_ANY
        )
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def flow_stats_reply_handler(self, ev):
        flows = []
        for stat in ev.msg.body:
            flows.append(
                {
                    "match": stat.match.to_jsondict(),
                    "actions": [
                        action.to_jsondict() for action in stat.instructions[0].actions
                    ],
                }
            )
        self.flows = flows
        self.lock.set()

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [
            parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)
        ]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(
                datapath=datapath,
                buffer_id=buffer_id,
                priority=priority,
                match=match,
                instructions=inst,
            )
        else:
            mod = parser.OFPFlowMod(
                datapath=datapath, priority=priority, match=match, instructions=inst
            )
        datapath.send_msg(mod)


if __name__ == "__main__":
    manager.main(args=[__file__, "--observe-links"])
