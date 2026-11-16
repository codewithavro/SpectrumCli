from abc import ABC, abstractmethod

from typing import List, Optional

from core.models import NetworkInfo, AdapterInfo

class ScannerBase(ABC):

    @abstractmethod

    def scan_networks(self) -> List[NetworkInfo]:
        """Discovers and returns a lise of nearby WI-FI  networks"""
        pass

    @abstractmethod

    def get_adapter_info(self) -> Optional[AdapterInfo]:
        """Retrieves local Wi-Fi adapter hardware and network connection info."""
        pass


    @abstractmethod

    def get_connected_network(self) -> Optional[NetworkInfo]:
        """Returns details of the currently connected Wi-Fi network."""
        pass