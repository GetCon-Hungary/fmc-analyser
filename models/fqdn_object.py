"""Represents the FQDN model."""

from fqdn import FQDN
from models.network_object import NetworkObject


class FQDNObject(NetworkObject):
    def __init__(self, id: str, name: str, value: str) -> None:
        super().__init__(id, name)
        self.value = FQDN(value)

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, FQDNObject):
            return self.value == __value.value
        return False

    def get_size(self) -> int:
        return 1
