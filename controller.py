import copy
import logging
from ryu.app.wsgi import WSGIApplication
from ryu.base import app_manager
from ryu.cmd import manager
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls, CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.ofproto import ofproto_v1_3
from ryu.topology import event
from ryu.topology.api import get_switch, get_link
from rest import RestController
from ryu.lib import hub
import utils


class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {"wsgi": WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.topology_api_app = self
        wsgi = kwargs["wsgi"]
        self.myapp = wsgi
        wsgi.register(RestController, {"controller": self})

        self.lock = hub.Event()
        self.flows = []

        self.orig_link_data = utils.load_data("sample1.txt")
        self.link_data = copy.deepcopy(self.orig_link_data)
        # self.link_data = utils.load_data("sample1.txt")

        self.hosts = {}  # h1: host object
        self.switches = {}  # dpid: datapath object
        self.adj = {}  # adjacency lists
        self.rules = {}  # dpid: flow rules

    def get_host_by_mac(self, host_mac):
        host_mac = host_mac.replace(":", "")
        return f"h{int(host_mac, 16)}"

    def get_host_by_ip(self, host_ipv4):
        for k, v in self.hosts.items():
            if v.ipv4 and host_ipv4 in v.ipv4:
                return k
        return None

    @set_ev_cls(event.EventHostAdd)
    def host_add_handler(self, ev):
        print(f"added {self.get_host_by_mac(ev.host.mac)}")
        self.hosts[self.get_host_by_mac(ev.host.mac)] = ev.host
        host_name, switch_name = (
            self.get_host_by_mac(ev.host.mac),
            f"s{ev.host.port.dpid}",
        )
        # each host connected to exactly one switch
        self.adj[host_name] = {switch_name}
        if switch_name not in self.adj:
            self.adj[switch_name] = {host_name}
        else:
            self.adj[switch_name].add(host_name)
        print("adj:", self.adj)

    @set_ev_cls(event.EventSwitchEnter)
    def switch_add_handler(self, ev):
        print(f"added s{ev.switch.dp.id}")
        self.switches[ev.switch.dp.id] = ev.switch.dp
        switch_name = f"s{ev.switch.dp.id}"
        links = get_link(self.topology_api_app, ev.switch.dp.id)
        links = {f"s{link.dst.dpid}" for link in links}

        for link in links.union({switch_name}):
            if link not in self.adj:
                self.adj[link] = set()

        self.adj[switch_name].update(links)
        for link in links:
            self.adj[link].add(switch_name)
        print("adj:", self.adj)

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

    def add_path_rules(self, path, req_bw, new_connection=False):
        rules = {}

        if len(path) < 3:
            return rules

        src, dst = self.hosts[path[0]], self.hosts[path[-1]]
        in_port = src.port.port_no
        for i in range(1, len(path) - 2):
            dpid = int(path[i][1:])
            links = get_link(self.topology_api_app, dpid)
            link = [link for link in links if link.dst.dpid == int(path[i + 1][1:])][0]
            if new_connection:
                rules[path[i]] = [
                    {
                        "match": {
                            "in_port": in_port,
                            "src_mac": src.mac,
                            "dst_mac": dst.mac,
                        },
                        "action": {
                            "out_port": link.src.port_no,
                        },
                    }
                ]
            else:
                dp = get_switch(self.topology_api_app, dpid)[0].dp
                self.add_rule(
                    datapath=dp,
                    in_port=in_port,
                    src_mac=src.mac,
                    dst_mac=dst.mac,
                    out_port=link.src.port_no,
                )
                self.link_data[(path[i - 1], path[i])][0] -= req_bw
                self.link_data[(path[i], path[i - 1])][0] -= req_bw
                rules[path[i]] = self.rules[dpid]

            in_port = link.dst.port_no

        dpid = int(path[-2][1:])
        if new_connection:
            rules[path[-2]] = [
                {
                    "match": {
                        "in_port": in_port,
                        "src_mac": src.mac,
                        "dst_mac": dst.mac,
                    },
                    "action": {
                        "out_port": dst.port.port_no,
                    },
                }
            ]
        else:
            dp = get_switch(self.topology_api_app, dpid)[0].dp
            self.add_rule(
                datapath=dp,
                in_port=in_port,
                src_mac=src.mac,
                dst_mac=dst.mac,
                out_port=dst.port.port_no,
            )
            self.link_data[(path[-3], path[-2])][0] -= req_bw
            self.link_data[(path[-2], path[-3])][0] -= req_bw
            rules[path[-2]] = self.rules[dpid]

            self.link_data[(path[-2], path[-1])][0] -= req_bw
            self.link_data[(path[-1], path[-2])][0] -= req_bw

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
        self.add_flow(datapath, 0)

    def add_flow(self, datapath, priority, buffer_id=None):
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
        action = parser.OFPActionOutput(
            ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER
        )

        instructions = [
            parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, [action])
        ]
        if buffer_id:
            mod = parser.OFPFlowMod(
                datapath=datapath,
                buffer_id=buffer_id,
                priority=priority,
                match=match,
                instructions=instructions,
            )
        else:
            mod = parser.OFPFlowMod(
                datapath=datapath,
                priority=priority,
                match=match,
                instructions=instructions,
            )
        datapath.send_msg(mod)


if __name__ == "__main__":
    manager.main(args=[__file__, "--observe-links"])
