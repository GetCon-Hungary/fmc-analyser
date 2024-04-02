"""Builds up all the different model classes."""

from typing import Union
from logic.fmc_loader import FMCLoader
from models.access_policy import AccessPolicy
from models.access_rule import AccessRule
from models.network import Network
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
        self.equal_object_finder(self.port_objs)

        self.network_objs: dict[str, NetworkObject] = {}
        self.network_objs.update(self.create_networks())
        self.network_objs.update(self.create_network_groups(self.fmcloader.network_groups['items']))
        self.equal_object_finder(self.network_objs)

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
                port_objs[port_id] = self._create_port(port)
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
        return port_grps

    def _create_port(self, port_obj: dict) -> Port:
        """Creates Port object.

        Args:
        ----
            port_obj: dictionary that represents a port.

        Returns:
        -------
            Port: Port object.

        """
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
                network_objs[network_id] = self._create_network(network)
        return network_objs

    def create_network_groups(self, network_groups: list[dict]) -> dict[str, NetworkGroup]:
        """Builds up the Network group dictionary.

        Args:
        ----
            network_groups: The list of Network group objects.

        Returns:
        -------
            dict[str, Network]: The dictionary of Network groups by id.

        """
        network_grps = {}
        for network in network_groups:
            network_id = network.get('id', None)
            if network_id is not None:
                group_name = network.get('name', None)
                network_group = NetworkGroup(network_id, group_name)
                if network.get('objects', None) is not None:
                    for network_obj in network['objects']:
                        network_type = network_obj['type']
                        if network_type == 'NetworkGroup':
                            net_grp = self.find_network_group_by_id(network_obj['id'])
                            group_result = self.create_network_groups([net_grp])
                            network_group.networks.extend(group_result.values())
                        else:
                            network_group.networks.append(self.network_objs[network_obj.get('id', None)])
                if network.get('literals', None) is not None:
                    for network_literal in network['literals']:
                        network_group.networks.append(self._create_network(network_literal))
                network_group.depth = network_group.get_network_depth()
                network_grps[network_id] = network_group
        return network_grps

    def find_network_group_by_id(self, id: str):
        """Finds Network group by id.

        Args:
        ----
            id: The id of a Network group.

        Returns:
        -------
            Network: The Network group object found by id.

        """
        for network in self.fmcloader.network_groups['items']:
            if network['id'] == id:
                return network
        return None

    def _create_network(self, network_obj: dict) -> Network:
        """Creates Network object.

        Args:
        ----
            network_obj: dictionary that represents a network.

        Returns:
        -------
            Network: Network object.

        """
        return Network(
            id=network_obj.get('id', ''),
            type=network_obj.get('type', ''),
            name=network_obj.get('name', ''),
            value=network_obj.get('value', ''),
        )

    def equal_object_finder(self, objs: dict[str, Union[NetworkObject, PortObject]]) -> None:
        """Finds the duplicated Network/Port objects.

        Args:
        ----
            objs: dictionary that contains Network or Port objects by id.

        """
        objs = list(objs.values())
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
            ac_rule_id = rule.get('id', None)
            name = rule.get('name', None)
            action = rule.get('action', None)
            enabled = rule.get('enabled', None)
            source_zones, destination_zones = self.get_zones_by_rule(rule)
            source_ports, destination_ports = self.get_ports_by_rule(rule)
            source_networks, destination_networks = self.get_networks_by_rule(rule)
            rules.append(AccessRule(
                ac_rule_id,
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
        return rules

    def get_zones_by_rule(self, rule: dict) -> tuple[list[str], list[str]]:
        """Gets zone names by rule.

        Args:
        ----
            rule: dictionary that represents an access rule.

        Returns:
        -------
            tuple[list[str], list[str]]: list of source and destination zone names.

        """
        s_zones = rule.get('sourceZones')
        d_zones = rule.get('destinationZones')
        s_zones_list = []
        d_zones_list = []
        if s_zones is not None:
            s_zones_list = [(s_zone['name']) for s_zone in s_zones['objects']]
        if d_zones is not None:
            d_zones_list = [(d_zone['name']) for d_zone in d_zones['objects']]
        return s_zones_list, d_zones_list

    def get_ports_by_rule(self, rule: dict) -> tuple[list[PortObject], list[PortObject]]:
        """Gets Ports object by rule.

        Args:
        ----
            rule: dictionary that represents an access rule.

        Returns:
        -------
            tuple[list[PortObject], list[PortObject]]: list of source and destination Port objects.

        """
        s_ports = rule.get('sourcePorts')
        d_ports = rule.get('destinationPorts')
        s_ports_list = []
        d_ports_list = []
        if s_ports is not None:
            s_objects = s_ports.get('objects', None)
            s_literals = s_ports.get('literals', None)
            if s_objects is not None:
                s_ports_list.extend(self.find_ports(s_objects))
            if s_literals is not None:
                s_ports_list.extend(self.find_ports(s_literals))
        if d_ports is not None:
            d_objects = d_ports.get('objects', None)
            d_literals = d_ports.get('literals', None)
            if d_objects is not None:
                d_ports_list.extend(self.find_ports(d_objects))
            if d_literals is not None:
                d_ports_list.extend(self.find_ports(d_literals))
        return s_ports_list, d_ports_list

    def find_ports(self, rule_ports: list[dict]) -> list[PortObject]:
        """Finds Port objects by rule.

        Args:
        ----
            rule: dictionary that represents a port.

        Returns:
        -------
            list[PortObject]: list of Port objects.

        """
        final = []
        for port in rule_ports:
            port_id = port.get('id', None)
            if port_id is not None:
                final.append(self.port_objs[port_id])
            else:
                final.append(self._create_port(port))
        return final

    def get_networks_by_rule(self, rule: dict) -> tuple[list[NetworkObject], list[NetworkObject]]:
        """Gets Networks object by rule.

        Args:
        ----
            rule: dictionary that represents an access rule.

        Returns:
        -------
            tuple[list[NetworkObject], list[NetworkObject]]: list of source and destination Network objects.

        """
        s_networks = rule.get('sourceNetworks')
        d_networks = rule.get('destinationNetworks')
        s_networks_list = []
        d_networks_list = []
        if s_networks is not None:
            s_objects = s_networks.get('objects', None)
            s_literals = s_networks.get('literals', None)
            if s_objects is not None:
                s_networks_list.extend(self.find_networks(s_objects))
            if s_literals is not None:
                s_networks_list.extend(self.find_networks(s_literals))
        if d_networks is not None:
            d_objects = d_networks.get('objects', None)
            d_literals = d_networks.get('literals', None)
            if d_objects is not None:
                d_networks_list.extend(self.find_networks(d_objects))
            if d_literals is not None:
                d_networks_list.extend(self.find_networks(d_literals))
        return s_networks_list, d_networks_list

    def find_networks(self, rule_networks: list[dict]) -> list[NetworkObject]:
        """Finds Network objects by rule.

        Args:
        ----
            rule: dictionary that represents a network.

        Returns:
        -------
            list[PortObject]: list of Network objects.

        """
        final = []
        for network in rule_networks:
            network_id = network.get('id', None)
            if network_id is not None:
                final.append(self.network_objs[network_id])
            else:
                final.append(self._create_network(network))
        return final