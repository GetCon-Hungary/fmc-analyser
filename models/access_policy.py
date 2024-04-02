"""Represents the access policy model."""
from models.access_rule import AccessRule
import math


class AccessPolicy:
    """Represents an access policy with a set of access rules."""

    def __init__(self, acp_id: str, name: str, rules: list[AccessRule]) -> None:  # noqa: D107
        self.id = acp_id
        self.name = name
        self.rules = rules

    def enabled_rules_count(self) -> int:  # noqa: D102
        count = 0
        for rule in self.rules:
            if rule.enabled:
                count += 1
        return count

    def allowed_rules_count(self) -> int:  # noqa: D102
        count = 0
        for rule in self.rules:
            if rule.action.lower() == 'allow':
                count += 1
        return count

    def allowed_rules_ratio(self) -> float:  # noqa: D102
        try:
            return (self.allowed_rules_count() / len(self.rules)) * 100
        except ZeroDivisionError:
            return float('NaN')

    def enabled_rules_ratio(self)-> float:  # noqa: D102
        try:
            return self.enabled_rules_count() / len(self.rules) * 100
        except ZeroDivisionError:
            return float('NaN')

    def calculate_avg_src_network_size_of_acp(self) -> int:  # noqa: D102
        number_of_ip_addresses = 0
        if len(self.rules) > 0:
            for rule in self.rules:
                number_of_ip_addresses += rule.get_source_networks_size()
            return int(number_of_ip_addresses / len(self.rules))
        return number_of_ip_addresses

    def calculate_avg_dst_network_size_of_acp(self) -> int:  # noqa: D102
        number_of_ip_addresses = 0
        if len(self.rules) > 0:
            for rule in self.rules:
                number_of_ip_addresses += rule.get_destination_network_size()
            return int(number_of_ip_addresses / len(self.rules))
        return number_of_ip_addresses

    def calculate_avg_dst_port_size_of_acp(self) -> int:  # noqa: D102
        number_of_ports = 0
        if len(self.rules) > 0:
            for rule in self.rules:
                number_of_ports += rule.get_destination_port_size()
            return int(number_of_ports / len(self.rules))
        return number_of_ports
    
    def _calculate_subnet_mask(self, ip_number: int) -> float:
        if ip_number > 0:
            mask = 32 - math.ceil(math.log2(ip_number))
            if mask > 0:
                return mask
            return 0
        return 0
