from ryu.topology.api import get_all_host, get_switch
from ryu.app.wsgi import ControllerBase, route
from ryu.controller import controller, dpset
from webob import Response
import json
import utils


class RestController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(RestController, self).__init__(req, link, data, **config)
        self.controller = data["controller"]

    # route to return all the links in the network and their associated cost.
    # In format <nodei-nodej>: <cost>
    @route("links", "/links", methods=["GET"])
    def get_links(self, req, **kwargs):
        links = self.controller.link_data
        links = {str(key): value for key, value in links.items()}
        links = json.dumps(links)

        print(links)
        return Response(json_body=links, content_type="application/json")

    # route to  ask from the user to select a host from where paths to all other hosts need to be computed.
    # Paths will be displayed as following:
    # Hi-Hj :Hi->Si->Sj->….->Hj
    @route("paths", "/paths/{host}", methods=["GET"])
    def get_paths(self, req, **kwargs):
        try:
            host = kwargs["host"]
            _, paths = utils.dijkstra(
                host, 0, self.controller.adj, self.controller.link_data
            )
            return Response(json_body=paths, content_type="application/json")
        except Exception as e:
            print(e)
            return Response(
                json_body={"error": str(e)}, content_type="application/json", status=400
            )

    @route("add_connection", "/add", methods=["POST"])
    def add_connection(self, req, **kwargs):
        id_spec = req.json.get("id_spec")
        src = req.json.get("src")
        dst = req.json.get("dst")
        req_bw = req.json.get("bw")

        print(id_spec, src, dst, req_bw)
        if id_spec == "ip":
            src = self.controller.get_host_by_ip(src)
            dst = self.controller.get_host_by_ip(dst)
        elif id_spec == "mac":
            src = self.controller.get_host_by_mac(src)
            dst = self.controller.get_host_by_mac(dst)

        dist, paths = utils.dijkstra(
            src, req_bw, self.controller.adj, self.controller.link_data
        )
        path = paths[dst]
        rules = self.controller.add_path_rules(path)
        print(rules)
        data = {"rules": rules, "path": path}
        return Response(json_body=data, content_type="application/json")

    # Only for veiwing purposes
    @route("flows", "/flows/{dpid}", methods=["GET"])
    def list_flows(self, req, **kwargs):
        dpid = int(kwargs["dpid"])
        dp = get_switch(self.controller.topology_api_app, dpid)[0].dp
        self.controller.send_flow_request(dp)
        self.controller.lock.wait()
        print(self.controller.flows)
        print(type(self.controller.flows))
        return Response(
            json_body=self.controller.flows, content_type="application/json"
        )
