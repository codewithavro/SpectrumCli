import json

import subprocess

from typing import List, Optional

from core.models import NetworkInfo, AdapterInfo

from core.scanner_base import ScannerBase

from platforms.android_termux.permission_check import TermuxPermissionChecker

class TermuxWifiScanner(ScannerBase):
    
    def scan_networks(self) -> List[NetworkInfo]:
        """Discovers and returns a list of nearby Wi-Fi networks using Termux-API."""
        is_valid, msg = TermuxPermissionChecker.verify_permissions()
        if not is_valid:
            raise PermissionError(msg)
        
        try:
            result = subprocess.run(
                ["termux-wifi-scaninfo"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            data = json.loads(result.stdout)
            networks = []
            
            for item in data:
                ssid = item.get("ssid", "")
                bssid = item.get("bssid", "00:00:00:00:00:00")
                rssi = item.get("rssi", -100)
                frequency = item.get("frequency", 2412)  # Frequency in MHz
                frequency_ghz = round(frequency / 1000.0, 1)
                
                # Approximate signal percentage from RSSI (-30 max, -100 min)
                signal_percent = max(0, min(100, int(2 * (rssi + 100)))) if rssi != 0 else 50
                
                # Calculate channel based on frequency
                channel = self._frequency_to_channel(frequency)
                
                # Security capabilities parsing
                capabilities = item.get("capabilities", item.get("security", "WPA2"))
                security = self._parse_security(capabilities)
                
                is_hidden = item.get("ssid_hidden", False) or not ssid.strip()

                networks.append(NetworkInfo(
                    ssid=ssid,
                    bssid=bssid,
                    signal_percent=signal_percent,
                    signal_dbm=rssi,
                    frequency_ghz=frequency_ghz,
                    channel=channel,
                    security=security,
                    is_hidden=is_hidden
                ))
            
            return networks
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to execute termux-wifi-scaninfo: {e.stderr}")
        except json.JSONDecodeError:
            raise ValueError("Failed to parse JSON output from termux-wifi-scaninfo.")

    def get_adapter_info(self) -> Optional[AdapterInfo]:
        """Retrieves local Wi-Fi connection metadata via termux-wifi-connectioninfo."""
        try:
            result = subprocess.run(
                ["termux-wifi-connectioninfo"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )
            data = json.loads(result.stdout)
            
            ssid = data.get("ssid", "")
            bssid = data.get("bssid", "00:00:00:00:00:00")
            ip_address = data.get("ip", None)
            mac_address = data.get("mac_address", bssid)
            
            state = "Connected" if ssid and ssid != "" else "Disconnected"

            return AdapterInfo(
                name="Android Wi-Fi Interface",
                description="Termux-API Mobile Wi-Fi Adapter",
                state=state,
                mac_address=mac_address,
                ip_address=ip_address,
                gateway_address=None,
                connected_ssid=ssid if state == "Connected" else None
            )
        except Exception:
            return None

    def get_connected_network(self) -> Optional[NetworkInfo]:
        """Returns details of the currently connected network."""
        adapter = self.get_adapter_info()
        if not adapter or adapter.state != "Connected" or not adapter.connected_ssid:
            return None
        
        networks = self.scan_networks()
        for net in networks:
            if net.ssid == adapter.connected_ssid:
                return net
        return None

    @staticmethod
    def _frequency_to_channel(frequency: int) -> int:
        """Converts frequency in MHz to standard Wi-Fi channel number."""
        if 2412 <= frequency <= 2484:
            if frequency == 2484:
                return 14
            return int((frequency - 2412) / 5) + 1
        elif 5170 <= frequency <= 5825:
            return int((frequency - 5180) / 5) + 36
        return 0

    @staticmethod
    def _parse_security(capabilities: str) -> str:
        """Parses security string from capabilities."""
        caps = capabilities.upper()
        if "WPA3" in caps:
            return "WPA3"
        elif "WPA2" in caps:
            return "WPA2"
        elif "WPA" in caps:
            return "WPA"
        elif "WEP" in caps:
            return "WEP"
        elif "ESS" in caps and "WPA" not in caps:
            return "Open"
        return caps if caps else "Unknown"