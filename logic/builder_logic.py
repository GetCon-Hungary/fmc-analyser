from typing import Union

from fmc_loader import FMCLoader
from models.access_policy import AccessPolicy
from models.access_rule import AccessRule
from models.network import Network
from models.network_group import NetworkGroup
from models.port import Port
from models.port_group import PortGroup


class Builder():
    def __init__(self, fmcloader: FMCLoader):
        self.fmcloader = fmcloader

        self.port_objs: dict[str, Union[Port, PortGroup]] = {}
        self.port_objs.update(self.create_protocol_ports(self.fmcloader.protocol_port_objs['items']))
        self.port_objs.update(self.create_port_groups(self.fmcloader.port_obj_groups['items']))
        self.equal_port_object_finder(self.port_objs)

        self.network_objs: dict[str, Union[Network, NetworkGroup]] = {}
        self.network_objs.update(self.create_networks(self.fmcloader.hosts['items']))
        self.network_objs.update(self.create_networks(self.fmcloader.networks['items']))
        self.network_objs.update(self.create_networks(self.fmcloader.ranges['items']))
        self.network_objs.update(self.create_network_groups(self.fmcloader.network_groups['items']))
        self.equal_network_object_finder(self.network_objs)

        self.policies: list[AccessPolicy] = self.create_access_policies(self.fmcloader.access_policies['items'])

    def create_protocol_ports(self, ports: list[dict]):
        port_objs = {}
        for port in ports:
            port_id = port.get('id', None)
            if port_id is not None:
                port_objs[port_id] = self._create_port(port)
        return port_objs

    def create_port_groups(self, port_groups: list[dict]):
        port_grps = {}
        for port in port_groups:
            port_id = port.get('id', None)
            if port_id is not None:
                group_name = port.get('name', None)
                port_group = PortGroup(port_id, group_name)
                for protocol_port in port['objects']:
                    port_group.ports.append(self.port_objs[protocol_port['id']])
                port_grps[port_id] = port_group
        return port_grps

    def _create_port(self, port_obj: dict):
        return Port(id=port_obj.get('id', None), name=port_obj.get('name', None), protocol=port_obj.get('protocol', None), port=port_obj.get('port', None))

    def equal_port_object_finder(self, ports_dict: dict[str, Union[Port, PortGroup]]):
        ports = list(ports_dict.values())
        for i in range(len(ports) - 1):
            for j in range(i + 1, len(ports)):
                if isinstance(ports[i], Port) and isinstance(ports[j], Port) and ports[i].__eq__(ports[j]):
                    ports[i].equal_with += "{}, ".format(ports[j].name)
                    ports[j].equal_with += "{}, ".format(ports[i].name)
                elif isinstance(ports[i], PortGroup) and isinstance(ports[j], PortGroup) and ports[i].__eq__(ports[j]):
                    ports[i].equal_with += "{}, ".format(ports[j].name)
                    ports[j].equal_with += "{}, ".format(ports[i].name)

    def create_networks(self, networks: list[dict]):
        network_objs = {}
        for network in networks:
            network_id = network.get('id', None)
            if network_id is not None:
                network_objs[network_id] = self._create_network(network)
        return network_objs

    def create_network_groups(self, network_groups: list[dict]):
        network_grps = {}
        for network in network_groups:
            network_id = network.get('id', None)
            if network_id is not None:
                group_name = network.get('name', None)
                network_group = NetworkGroup(network_id, group_name)
                if network.get('objects', None) is not None:
                    for network_obj in network['objects']:
                        network_type = network_obj['type']
                        if network_type == "NetworkGroup":
                            net_grp = self.find_network_group_by_id(network_obj['id'])
                            group_result = self.create_network_groups(net_grp)
                            network_group.networks.extend(group_result.values())
                        else:
                            network_group.networks.append(self.network_objs[network_obj.get('id', None)])
                    network_group.depth = network_group.get_network_depth()
                if network.get('literals', None) is not None:
                    for network_literal in network['literals']:
                        network_group.networks.append(self._create_network(network_literal))
                network_grps[network_id] = network_group

        return network_grps

    def find_network_group_by_id(self, id: str):
        for network in self.fmcloader.network_groups['items']:
            if network['id'] == id:
                return [network]
        return []

    def _create_network(self, network_obj: dict):
        return Network(id=network_obj.get('id', None), type=network_obj.get('type', None), name=network_obj.get('name', None), value=network_obj.get('value', None))

    def equal_network_object_finder(self, objs_dict: dict[str, Union[Network, NetworkGroup]]):
        objs = list(objs_dict.values())
        for i in range(len(objs) - 1):
            for j in range(i + 1, len(objs)):
                if isinstance(objs[i], Network) and isinstance(objs[j], Network) and objs[i].__eq__(objs[j]):
                    objs[i].equal_with += "{}, ".format(objs[j].name)
                    objs[j].equal_with += "{}, ".format(objs[i].name)
                elif isinstance(objs[i], NetworkGroup) and isinstance(objs[j], NetworkGroup):
                    obj_i = objs[i].flat_network_object_grp()
                    obj_j = objs[j].flat_network_object_grp()
                    if obj_i.__eq__(obj_j):
                        objs[i].equal_with += "{}, ".format(objs[j].name)
                        objs[j].equal_with += "{}, ".format(objs[i].name)

    def create_access_policies(self, acps: list[dict]):
        policies = []
        for acp in acps:
            id = acp.get('id', None)
            name = acp.get('name', None)
            rules = self.create_access_rules(self.fmcloader.access_rules[name]['items'])
            policies.append(AccessPolicy(id, name, rules))
        return policies

    def create_access_rules(self, accessrules: list[dict]):
        rules = []
        for rule in accessrules:
            id = rule.get('id', None)
            name = rule.get('name', None)
            action = rule.get('action', None)
            enabled = rule.get('enabled', None)
            source_zones, destination_zones = self.get_zones_by_rule(rule)
            source_ports, destination_ports = self.get_ports_by_rule(rule)
            source_networks, destination_networks = self.get_networks_by_rule(rule)
            rules.append(AccessRule(id, name, action, enabled, source_networks, source_zones, source_ports, destination_networks, destination_zones, destination_ports))
        return rules

    def get_zones_by_rule(self, rule: dict):
        s_zones = rule.get('sourceZones', None)
        d_zones = rule.get('destinationZones', None)
        s_zones_list = []
        d_zones_list = []
        if s_zones is not None:
            s_zones_list = [(s_zone['name']) for s_zone in s_zones['objects']]
        if d_zones is not None:
            d_zones_list = [(d_zone['name']) for d_zone in d_zones['objects']]
        return s_zones_list, d_zones_list

    def get_ports_by_rule(self, rule: dict):
        s_ports = rule.get('sourcePorts', None)
        d_ports = rule.get('destinationPorts', None)
        s_ports_list = []
        d_ports_list = []
        if s_ports is not None:
            s_objects = s_ports.get('objects', None)
            s_literals = s_ports.get('literals', None)
            if s_objects is not None:
                s_ports_list.extend(self.find_port_by_id(s_objects))
            if s_literals is not None:
                s_ports_list.extend(self.find_port_by_id(s_literals))
        if d_ports is not None:
            d_objects = d_ports.get('objects', None)
            d_literals = d_ports.get('literals', None)
            if d_objects is not None:
                d_ports_list.extend(self.find_port_by_id(d_objects))
            if d_literals is not None:
                d_ports_list.extend(self.find_port_by_id(d_literals))
        return s_ports_list, d_ports_list

    def find_port_by_id(self, rule_ports: list[dict]):
        final = []
        for port in rule_ports:
            port_id = port.get('id', None)
            if port_id is not None:
                final.append(self.port_objs[port_id])
            else:
                final.append(self._create_port(port))
        return final

    def get_networks_by_rule(self, rule: dict):
        s_networks = rule.get('sourceNetworks', None)
        d_networks = rule.get('destinationNetworks', None)
        s_networks_list = []
        d_networks_list = []
        if s_networks is not None:
            s_objects = s_networks.get('objects', None)
            s_literals = s_networks.get('literals', None)
            if s_objects is not None:
                s_networks_list.extend(self.find_network_by_id(s_objects))
            if s_literals is not None:
                s_networks_list.extend(self.find_network_by_id(s_literals))
        if d_networks is not None:
            d_objects = d_networks.get('objects', None)
            d_literals = d_networks.get('literals', None)
            if d_objects is not None:
                d_networks_list.extend(self.find_network_by_id(d_objects))
            if d_literals is not None:
                d_networks_list.extend(self.find_network_by_id(d_literals))
        return s_networks_list, d_networks_list

    def find_network_by_id(self, rule_networks: list[dict]):
        final = []
        for network in rule_networks:
            network_id = network.get('id', None)
            if network_id is not None:
                final.append(self.network_objs[network_id])
            else:
                final.append(self._create_network(network))

        return final
