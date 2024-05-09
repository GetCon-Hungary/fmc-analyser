"""Represents the range model."""

from netaddr import IPRange

from models.network_object import NetworkObject


class Range(NetworkObject):
    def __init__(self, id: str, name: str, value: str) -> None:
        super().__init__(id, name)
        self.value = IPRange(value.split('-')[0], value.split('-')[1])

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Range):
            return self.value == __value.value
        return False

    def get_size(self) -> int:
        return self.value.size
