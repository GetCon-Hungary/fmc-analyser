"""Parses data from models into easy-to-use format for Pandas."""

import yaml

from logic.builder_logic import Builder
from models.network import Network
from models.network_group import NetworkGroup
from models.network_object import NetworkObject
from models.port import Port
from models.port_group import PortGroup
from models.port_object import PortObject


class Data:
    def __init__(self, builder: Builder, config) -> None:  # noqa:D107
        self.builder = builder
        with open(config, encoding='utf-8') as cfg:
            self.config = yaml.safe_load(cfg)
        self.ports_data = self.get_ports_data()
        self.networks_data = self.get_networks_data()
        self.access_rules_data = self.get_access_rules_data()
        self.access_policies_data = self.get_access_policy_data()

    def get_access_policy_data(self) -> list:
        """Creates the access policy data for export.

        Returns:
        -------
            list[str]: The list of access policy data.

        """
        return [(
            policy.name,
            policy.enabled_rules_count(),
            policy.allowed_rules_count(),
            '{}%'.format(policy.enabled_rules_ratio()),
            '{}%'.format(policy.allowed_rules_ratio()),
            policy.calculate_avg_src_network_size_of_acp(),
            '/{}'.format(policy._calculate_subnet_mask(policy.calculate_avg_src_network_size_of_acp())),
            policy.calculate_avg_dst_network_size_of_acp(),
            '/{}'.format(policy._calculate_subnet_mask(policy.calculate_avg_dst_network_size_of_acp())),
            policy.calculate_avg_dst_port_size_of_acp()) for policy in self.builder.policies]

    def get_access_rules_data(self) -> dict[str, list]:
        """Creates the access rules data for export.

        Returns:
        -------
            dict[str, list]: The dictionary of access rules data by access policy names.

        """
        access_rule_data = {}
        for policy in self.builder.policies:
            avg_src_ip_num = policy.calculate_avg_src_network_size_of_acp()
            avg_dst_ip_num = policy.calculate_avg_dst_network_size_of_acp()
            avg_port_number = policy.calculate_avg_dst_port_size_of_acp()
            access_rule_data[policy.name] = [(
                rule.name,
                rule.action,
                rule.enabled,
                self._get_zones_data_by_rule(rule.source_zones),
                self._get_networks_data_by_rule(rule.source_networks),
                self._get_ports_data_by_rule(rule.source_ports),
                self._get_zones_data_by_rule(rule.destination_zones),
                self._get_networks_data_by_rule(rule.destination_networks),
                self._get_ports_data_by_rule(rule.destination_ports),
                rule.get_source_networks_size() if rule.get_source_networks_size() > 0 else 4294967296,
                '/{}'.format(rule._calculate_subnet_mask(rule.get_source_networks_size())),
                rule.get_destination_network_size() if rule.get_destination_network_size() > 0 else 4294967296,
                '/{}'.format(rule._calculate_subnet_mask(rule.get_destination_network_size())),
                rule.get_destination_port_size() if rule.get_destination_port_size() > 0 else 65535,
                rule.risk_category_by_src_network_static(self.config['SOURCE_NETWORK_CATEGORIES']),
                rule.risk_category_by_source_network_dynamic(avg_src_ip_num, self.config['RELATIVE_SOURCE_NETWORK_CATEGORIES']),
                rule.risk_category_by_dst_network_static(self.config['DESTINATION_NETWORK_CATEGORIES']),
                rule.risk_category_by_dst_network_dynamic(avg_dst_ip_num, self.config['RELATIVE_DESTINATION_NETWORK_CATEGORIES']),
                rule.risk_category_by_dst_port_static(self.config['DESTINATION_PORT_CATEGORIES']),
                rule.risk_category_by_destination_port_dynamic(avg_port_number, self.config['RELATIVE_DESTINATION_PORT_CATEGORIES']),
                ', '.join(eq.name for eq in rule.equal_with),
                ', '.join(rev.name for rev in rule.rev_eq))
            for rule in policy.rules]
        return access_rule_data

    def _get_zones_data_by_rule(self, zones: list[str]) -> str:
        """Gets zones name by rule.

        Args:
        ----
            zones: list of zone names.

        Returns:
        -------
            str: Returns the elements in the list separated by commas, or 'Any' if the list length is 0.

        """
        if len(zones) > 0:
            return ', '.join(zones)
        else:
            return 'Any'

    def _get_ports_data_by_rule(self, ports: list[PortObject]) -> str:
        """Gets ports data by rule..

        Args:
        ----
            zones: list of Port objects.

        Returns:
        -------
            str: Returns the name of Port objects in the list separated by commas, or 'Any' if the list length is 0.

        """
        if len(ports) > 0:
            return ', '.join(port.name if port.name != '' else port.port for port in ports)
        else:
            return 'Any'

    def _get_networks_data_by_rule(self, networks: list[NetworkObject]) -> str:
        """Gets networks data by rule..

        Args:
        ----
            zones: list of Network objects.

        Returns:
        -------
            str: Returns the name of Network objects in the list separated by commas, or 'Any' if the list length is 0.

        """
        if len(networks) > 0:
            return ', '.join(network.name if network.name != '' else str(network.value) for network in networks)
        else:
            return 'Any'

    def get_ports_data(self) -> list:
        """Creates the ports data for export.

        Returns:
        -------
            list: The list of ports data.

        """
        ports_data = []
        ports_count = self.get_port_object()
        for port_obj in self.builder.port_objs.values():
            if isinstance(port_obj, Port):
                ports_data.append((None, port_obj.name, port_obj.protocol, port_obj.port, port_obj.size, str(port_obj._is_risky_port(self.config['HIGH_RISK_PROTOCOLS'])), self.get_equal_ports_data(port_obj.equal_with), ports_count[port_obj.id]))
            elif isinstance(port_obj, PortGroup):
                names, protocols, ports, port_risks = "", "", "", ""
                for port in port_obj.flat_port_object_grp():
                    names += '{}\n'.format(port.name)
                    protocols += '{}\n'.format(port.protocol)
                    ports += '{}\n'.format(port.port)
                    port_risks += '{}\n'.format(port._is_risky_port(self.config['HIGH_RISK_PROTOCOLS']))
                ports_data.append((port_obj.name, names.strip(), protocols.strip(), ports.strip(), port_obj.get_size(), port_risks.strip(), self.get_equal_ports_data(port_obj.equal_with), ports_count[port_obj.id]))
        return ports_data

    def get_equal_ports_data(self, ports: list[PortObject]) -> str:
        """Gets equal ports data

        Args:
        ----
            zones: list of Port objects.

        Returns:
        -------
            str: Returns the name of Port objects in the list separated by commas.

        """
        return ', '.join(port.name for port in ports)

    def get_port_object(self) -> dict:
        """Builds up the dictionary that contains the appearance of Port object in Access rules.

        Returns:
        ----
            dict: dictionary that contains the Port's id and an integer that represents the number of appearance.

        """
        ports = {}
        for port in self.builder.port_objs.values():
            ports[port.id] = 0
        self.port_object_count(ports)
        return ports

    def port_object_count(self, ports: dict[str, int]) -> None:
        """It counts how many times the given Port object appears in the Access rules.

        Args:
        ----
            ports: dictionary that contains the Port's id and an integer that represents the number of appearance.

        """
        for policy in self.builder.policies:
            for rule in policy.rules:
                for key in ports:
                    if rule.port_used_in_rule(key):
                            ports[key] += 1
                            port = self.builder.port_objs.get(key, None)
                            if isinstance(port, PortGroup):
                                for flat in port.flat_port_object_grp():
                                    if flat.id != '':
                                        ports[flat.id] += 1

    def get_networks_data(self) -> list:
        """Create the networks data for export.

        Returns:
        -------
            list: The list of networks data.

        """
        networks_data = []
        networks_count = self.get_network_object()
        for network_obj in self.builder.network_objs.values():
            if isinstance(network_obj, Network):
                networks_data.append((None, None, network_obj.name, str(network_obj.value), network_obj.get_size(), '/{}'.format(str(network_obj.value).split('/')[1]), self.get_equal_networks_data(network_obj.equal_with), networks_count[network_obj.id]))
            elif isinstance(network_obj, NetworkGroup):
                names, ips = "", ""
                for network in network_obj.flat_network_object_grp():
                    names += '{}\n'.format(network.name)
                    ips += '{}\n'.format(str(network.value))
                networks_data.append((network_obj.name, network_obj.depth, names.strip(), ips.strip(), network_obj.get_size(), '/{}'.format(network_obj._calculate_subnet_mask(network_obj.get_size())), self.get_equal_networks_data(network_obj.equal_with), networks_count[network_obj.id]))
        return networks_data

    def get_equal_networks_data(self, networks: list[NetworkObject]) -> str:
        """Gets equal networks data

        Args:
        ----
            zones: list of Network objects.

        Returns:
        -------
            str: Returns the name of Network objects in the list separated by commas.

        """
        return ', '.join(network.name for network in networks)

    def get_network_object(self) -> dict:
        """Builds up the dictionary that contains the appearance of Network object in Access rules.

        Returns:
        ----
            dict: dictionary that contains the Network's id and an integer that represents the number of appearance.

        """
        networks = {}
        for network in self.builder.network_objs.values():
            networks[network.id] = 0
        self.network_object_count(networks)
        return networks

    def network_object_count(self, networks: dict[str, int]) -> None:
        """It counts how many times the given Network object appears in the Access rules.

        Args:
        ----
            ports: dictionary that contains the Network's id and an integer that represents the number of appearance.

        """
        for policy in self.builder.policies:
            for rule in policy.rules:
                for key in networks:
                    if rule.network_used_in_rule(key):
                            networks[key] += 1
                            network = self.builder.network_objs.get(key, None)
                            if isinstance(network, NetworkGroup):
                                for flat in network.flat_network_object_grp():
                                    if flat.id != '':
                                        networks[flat.id] += 1