"""Represents the access policy model."""
from models.access_rule import AccessRule


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
    
    def _calculate_subnet_mask(self, ip_number: int) -> int:
        # Initialize a mask
        mask = 0x80000000  # 0b10000000000000000000000000000000

        # Find the leftmost set bit
        position = 32
        while position >= 0:
            if ip_number - mask > 0:
                half_mask = mask >> 1
                if ip_number - mask - half_mask >= 0:
                    return 32 - position
                else:
                    return 32 - (position - 1)
            mask >>= 1
            position -= 1
        
        return 0