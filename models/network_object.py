"""Represents the network object model."""
import abc


class NetworkObject():
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name
        self.equal_with = []

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

    @abc.abstractmethod
    def get_size(self) -> int:
        pass
    
    @abc.abstractmethod
    def __eq__(self, value: object) -> bool:
        pass
