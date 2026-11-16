from dataclasses import dataclass, field

from typing import Optional, List

@dataclass

class NetworkInfo:

    ssid: str

    bssid: str

    signal_percent: int # 0 to 100

    signal_dbm: int #e.g., -30 to -90 dBm

    frequency_ghz: float # 2.4, 5.0, or 6.0

    channel: int

    security: str # WPA2, WPA3, Open, WEP, etc.

    is_hidden: bool = False

    def __lt__(self, other):
        # Higher signal_dbm (closer to 0) means stronger signal

        return self.signal_dbm > other.signal_dbm
    
@dataclass

class AdapterInfo:

    name: str

    description: str

    state : str

    mac_address: str

    ip_address: Optional[str] = None

    gateway_address: Optional[str] = None

    connected_ssid: Optional[str] = None