"""Builds up all the different model classes."""

from typing import Union
from logic.fmc_loader import FMCLoader
from models.access_policy import AccessPolicy
from models.access_rule import AccessRule
from models.network import Network
from models.host import Host
from models.range import Range
from models.network_group import NetworkGroup
from models.network_object import NetworkObject
from models.port import Port
from models.port_group import PortGroup
from models.port_object import PortObject


class Builder:
    def __init__(self, fmcloader: FMCLoader) -> None:  # noqa: D107
        self.fmcloader = fmcloader

        self.port_objs: dict[str, PortObject] = {}
        self.port_objs.update(self.create_protocol_ports())
        self.port_objs.update(self.create_port_groups())

        self.network_objs: dict[str, NetworkObject] = {}
        self.network_objs.update(self.create_networks())
        self.network_objs.update(self.create_network_groups())

        self.policies: list[AccessPolicy] = self.create_access_policies()

    def create_protocol_ports(self) -> dict[str, Port]:  # noqa: D102
        """Builds up the Port dictionary.

        Returns:
        -------
            dict[str, Port]: The dictionary of Ports by id.

        """
        port_objs = {}
        for port in self.fmcloader.protocol_port_objs['items']:
            port_id = port.get('id', None)
            if port_id is not None:
                port_objs[port_id] = self.__create_port(port)
        self.__equal_object_finder(list(port_objs.values()))
        return port_objs

    def create_port_groups(self) -> dict[str, PortGroup]:
        """Builds up the Port group dictionary.

        Returns:
        -------
            dict[str, PortGroup]: The dictionary of Port groups by id.

        """
        port_grps = {}
        for port in self.fmcloader.port_obj_groups['items']:
            port_id = port.get('id', None)
            if port_id is not None:
                group_name = port.get('name', None)
                port_group = PortGroup(port_id, group_name)
                for protocol_port in port['objects']:
                    port_group.ports.append(self.port_objs[protocol_port['id']])
                port_grps[port_id] = port_group
        self.__equal_object_finder(list(port_grps.values()))
        return port_grps

    def __create_port(self, port_obj: dict) -> Port:
        return Port(
            id=port_obj.get('id', ''),
            name=port_obj.get('name', ''),
            protocol=port_obj.get('protocol', ''),
            port=port_obj.get('port', ''),
        )

    def create_networks(self) -> dict[str, Network]:
        """Builds up the Network dictionary.

        Returns:
        -------
            dict[str, Network]: The dictionary of Networks by id.

        """
        network_objs = {}
        for network in self.fmcloader.networks['items']:
            network_id = network.get('id', None)
            if network_id is not None:
                network_objs[network_id] = self.__create_network(network)
        self.__equal_object_finder(list(network_objs.values()))
        return network_objs

    def create_network_groups(self) -> dict[str, NetworkGroup]:
        """Builds up the Network group dictionary.

        Args:
        ----
            network_groups: The list of Network group objects.

        Returns:
        -------
            dict[str, Network]: The dictionary of Network groups by id.

        """
        network_grps = {}
        for network_grp in self.fmcloader.network_groups['items']:
            group_id = network_grp.get('id', None)
            if group_id is not None:
                network_group = self.__recursive_network_group(network_grp)
                network_grps[group_id] = network_group
        self.__equal_object_finder(list(network_grps.values()))
        return network_grps
    
    def __recursive_network_group(self, net_group: dict) -> NetworkGroup:
        group_id = net_group.get('id', None)
        if group_id is not None:
            group_name = net_group.get('name', None)
            network_group = NetworkGroup(group_id, group_name)
            if net_group.get('objects', None) is not None:
                for network_obj in net_group['objects']:
                    network_type = network_obj['type']
                    if network_type == 'NetworkGroup':
                        net_grp = self.__find_network_group_by_id(network_obj['id'])
                        group_result = self.__recursive_network_group(net_grp)
                        network_group.networks.append(group_result)
                    else:
                        network_group.networks.append(self.network_objs[network_obj.get('id', None)])
            if net_group.get('literals', None) is not None:
                for network_literal in net_group['literals']:
                        network_group.networks.append(self.__create_network(network_literal))
            network_group.depth = network_group.get_network_depth()
        return network_group
            
    def __find_network_group_by_id(self, id: str):
        for network in self.fmcloader.network_groups['items']:
            if network['id'] == id:
                return network
        return None

    def __create_network(self, network_obj: dict) -> Network:
        type = network_obj.get('type', '')
        if type == 'Host':
            return Host(id=network_obj.get('id', ''), name=network_obj.get('name', ''), value=network_obj.get('value', ''))
        elif type == 'Range':
            return Range(id=network_obj.get('id', ''), name=network_obj.get('name', ''), value=network_obj.get('value', ''))
        elif type == 'Network':
            return Network(id=network_obj.get('id', ''), name=network_obj.get('name', ''), value=network_obj.get('value', ''))
        else:
            raise TypeError
    
    def __reverse_equal_object_finder(self, rules: list[AccessRule]) -> None:
        for i in range(len(rules) - 1):
            for j in range(i + 1, len(rules)):
                if rules[i].reverse_eq(rules[j]):
                    rules[i].rev_eq.append(rules[j])
                    rules[j].rev_eq.append(rules[i])
    
    def __merge_candidates_object_finder(self, rules: list[AccessRule]) -> None:
        for i in range(len(rules) - 1):
            for j in range(i + 1, len(rules)):
                if rules[i].merge_candidates(rules[j]):
                    rules[i].merge_can.append(rules[j])
                    rules[j].merge_can.append(rules[i])
        
    def __equal_object_finder(self, objs: list[Union[NetworkObject, PortObject, AccessRule]]) -> None:
        for i in range(len(objs) - 1):
            for j in range(i + 1, len(objs)):
                if objs[i] == objs[j]:
                    objs[i].equal_with.append(objs[j])
                    objs[j].equal_with.append(objs[i])

    def create_access_policies(self) -> list[AccessPolicy]:
        """Builds up the Access policy list.

        Returns:
        -------
            list[AccessPolicy]: The list of access policies.

        """
        policies = []
        for acp in self.fmcloader.access_policies['items']:
            acp_id = acp.get('id', None)
            name = acp.get('name', None)
            rules = self.create_access_rules(name)
            policies.append(AccessPolicy(acp_id, name, rules))
        return policies

    def create_access_rules(self, acp_name) -> list[AccessRule]:
        """Builds up the Access rules list.

        Args:
        ----
            acp_name: the name of the Access policy.

        Returns:
        -------
            list[AccessRule]: The list of access rules.

        """
        rules = []
        for rule in self.fmcloader.access_rules[acp_name]['items']:
            id = rule.get('id', None)
            name = rule.get('name', None)
            action = rule.get('action', None)
            enabled = rule.get('enabled', None)
            source_zones, destination_zones = self.__get_zones_by_rule(rule)
            source_ports, destination_ports = self.__get_ports_by_rule(rule)
            source_networks, destination_networks = self.__get_networks_by_rule(rule)
            rules.append(AccessRule(
                id,
                name,
                action,
                enabled,
                source_networks,
                source_zones,
                source_ports,
                destination_networks,
                destination_zones,
                destination_ports,
            ))
        self.__equal_object_finder(rules)
        self.__reverse_equal_object_finder(rules)
        self.__merge_candidates_object_finder(rules)
        return rules

    def __get_zones_by_rule(self, rule: dict) -> tuple[list[str], list[str]]:
        s_zones = rule.get('sourceZones')
        d_zones = rule.get('destinationZones')
        s_zones_list = []
        d_zones_list = []
        if s_zones is not None:
            s_zones_list = [(s_zone['name']) for s_zone in s_zones['objects']]
            s_zones_list.sort()
        if d_zones is not None:
            d_zones_list = [(d_zone['name']) for d_zone in d_zones['objects']]
            d_zones_list.sort()

        return s_zones_list, d_zones_list

    def __get_ports_by_rule(self, rule: dict) -> tuple[list[PortObject], list[PortObject]]:
        s_ports = rule.get('sourcePorts')
        d_ports = rule.get('destinationPorts')
        s_ports_list = []
        d_ports_list = []
        if s_ports is not None:
            s_objects = s_ports.get('objects', None)
            s_literals = s_ports.get('literals', None)
            if s_objects is not None:
                s_ports_list.extend(self.__find_ports(s_objects))
            if s_literals is not None:
                s_ports_list.extend(self.__find_ports(s_literals))
            s_ports_list.sort(key=lambda x: x.name)
        if d_ports is not None:
            d_objects = d_ports.get('objects', None)
            d_literals = d_ports.get('literals', None)
            if d_objects is not None:
                d_ports_list.extend(self.__find_ports(d_objects))
            if d_literals is not None:
                d_ports_list.extend(self.__find_ports(d_literals))
            d_ports_list.sort(key=lambda x: x.name)

        return s_ports_list, d_ports_list

    def __find_ports(self, rule_ports: list[dict]) -> list[PortObject]:
        final = []
        for port in rule_ports:
            port_id = port.get('id', None)
            if port_id is not None:
                final.append(self.port_objs[port_id])
            else:
                final.append(self.__create_port(port))
        return final

    def __get_networks_by_rule(self, rule: dict) -> tuple[list[NetworkObject], list[NetworkObject]]:
        s_networks = rule.get('sourceNetworks')
        d_networks = rule.get('destinationNetworks')
        s_networks_list = []
        d_networks_list = []
        if s_networks is not None:
            s_objects = s_networks.get('objects', None)
            s_literals = s_networks.get('literals', None)
            if s_objects is not None:
                s_networks_list.extend(self.__find_networks(s_objects))
            if s_literals is not None:
                s_networks_list.extend(self.__find_networks(s_literals))
            s_networks_list.sort(key=lambda x: x.name)
        if d_networks is not None:
            d_objects = d_networks.get('objects', None)
            d_literals = d_networks.get('literals', None)
            if d_objects is not None:
                d_networks_list.extend(self.__find_networks(d_objects))
            if d_literals is not None:
                d_networks_list.extend(self.__find_networks(d_literals))
            d_networks_list.sort(key=lambda x: x.name)

        return s_networks_list, d_networks_list

    def __find_networks(self, rule_networks: list[dict]) -> list[NetworkObject]:
        final = []
        for network in rule_networks:
            network_id = network.get('id', None)
            if network_id is not None:
                final.append(self.network_objs[network_id])
            else:
                final.append(self.__create_network(network))
        return final