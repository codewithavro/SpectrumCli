import ctypes
import re
import subprocess
import time
from typing import List, Optional

from core.models import AdapterInfo, NetworkInfo
from core.scanner_base import ScannerBase
from platforms.windows.adapter_info import WindowsAdapterInfo


class WindowsWlanScanner(ScannerBase):

    def _trigger_hardware_scan(self) -> None:
        """Uses Windows Native Wifi API (wlanapi.dll) to trigger an active Wi-Fi scan."""
        try:
            wlanapi = ctypes.windll.wlanapi
            negotiated_version = ctypes.c_ulong()
            client_handle = ctypes.c_void_p()

            if wlanapi.WlanOpenHandle(2, None, ctypes.byref(negotiated_version), ctypes.byref(client_handle)) != 0:
                return

            class GUID(ctypes.Structure):
                _fields_ = [
                    ("Data1", ctypes.c_ulong),
                    ("Data2", ctypes.c_ushort),
                    ("Data3", ctypes.c_ushort),
                    ("Data4", ctypes.c_ubyte * 8),
                ]

            class WLAN_INTERFACE_INFO(ctypes.Structure):
                _fields_ = [
                    ("InterfaceGuid", GUID),
                    ("strInterfaceDescription", ctypes.c_wchar * 256),
                    ("isState", ctypes.c_int),
                ]

            class WLAN_INTERFACE_INFO_LIST(ctypes.Structure):
                _fields_ = [
                    ("dwNumberOfItems", ctypes.c_ulong),
                    ("dwIndex", ctypes.c_ulong),
                    ("InterfaceInfo", WLAN_INTERFACE_INFO * 1),
                ]

            p_list = ctypes.POINTER(WLAN_INTERFACE_INFO_LIST)()
            if wlanapi.WlanEnumInterfaces(client_handle, None, ctypes.byref(p_list)) == 0:
                num_interfaces = p_list.contents.dwNumberOfItems
                interfaces_array = ctypes.cast(
                    ctypes.addressof(p_list.contents.InterfaceInfo),
                    ctypes.POINTER(WLAN_INTERFACE_INFO * num_interfaces),
                ).contents

                for iface in interfaces_array:
                    wlanapi.WlanScan(client_handle, ctypes.byref(iface.InterfaceGuid), None, None, None)

                wlanapi.WlanFreeMemory(p_list)
                # Wait for adapter to collect beacons across 2.4 GHz, 5 GHz, and 6 GHz channels
                time.sleep(2.5)

            wlanapi.WlanCloseHandle(client_handle, None)
        except Exception:
            pass

    def scan_networks(self) -> List[NetworkInfo]:
        """Discovers and returns all nearby Wi-Fi networks and BSSIDs using Windows netsh wlan."""
        self._trigger_hardware_scan()
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "networks", "mode=bssid"],
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
                errors="ignore",
            )
            return self._parse_netsh_output(result.stdout)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to execute netsh wlan command: {e.stderr}")
        except Exception as e:
            raise RuntimeError(f"Error scanning Wi-Fi networks on Windows: {str(e)}")

    def get_adapter_info(self) -> Optional[AdapterInfo]:
        """Retrieves local Wi-Fi adapter connection information."""
        return WindowsAdapterInfo.get_adapter_details()

    def get_connected_network(self) -> Optional[NetworkInfo]:
        """Returns details of the currently connected Wi-Fi network."""
        adapter = self.get_adapter_info()
        if not adapter or not adapter.connected_ssid:
            return None

        networks = self.scan_networks()
        for net in networks:
            if net.ssid == adapter.connected_ssid:
                return net
        return None

    def _parse_netsh_output(self, output: str) -> List[NetworkInfo]:
        """
        Parses complete netsh output without missing any SSID or multiple BSSIDs per SSID.
        """
        networks: List[NetworkInfo] = []
        blocks = re.split(r"\n(?=\s*SSID\s+\d+\s*:\s*)", output)

        for block in blocks:
            if "SSID" not in block:
                continue

            lines = [line.strip() for line in block.splitlines() if line.strip()]

            ssid = ""
            security = "Open"
            is_hidden = False
            bssids: List[dict] = []
            current_bssid: Optional[dict] = None

            for line in lines:
                # Match SSID line (excluding BSSID lines)
                if re.match(r"^SSID\s+\d+\s*:", line, re.IGNORECASE):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        ssid = parts[1].strip()
                elif line.startswith("Authentication") or line.startswith("Security"):
                    if "WPA3" in line:
                        security = "WPA3"
                    elif "WPA2" in line:
                        security = "WPA2"
                    elif "WPA" in line:
                        security = "WPA"
                    elif "WEP" in line:
                        security = "WEP"
                    elif "Open" in line:
                        security = "Open"
                elif re.match(r"^BSSID\s+\d+\s*:", line, re.IGNORECASE):
                    if current_bssid:
                        bssids.append(current_bssid)
                    bssid_match = re.search(r"BSSID\s*\d*\s*:\s*([0-9a-fA-F:-]+)", line, re.IGNORECASE)
                    current_bssid = {
                        "bssid": bssid_match.group(1).strip() if bssid_match else "00:00:00:00:00:00",
                        "signal_percent": 0,
                        "signal_dbm": -100,
                        "channel": 1,
                        "frequency_ghz": 2.4,
                    }
                elif current_bssid is not None:
                    if line.startswith("Signal"):
                        sig_match = re.search(r"Signal\s*:\s*(\d+)%", line, re.IGNORECASE)
                        if sig_match:
                            pct = int(sig_match.group(1))
                            current_bssid["signal_percent"] = pct
                            current_bssid["signal_dbm"] = int((pct / 2) - 100)
                    elif line.startswith("Channel"):
                        chan_match = re.search(r"Channel\s*:\s*(\d+)", line, re.IGNORECASE)
                        if chan_match:
                            ch = int(chan_match.group(1))
                            current_bssid["channel"] = ch
                            if ch <= 14:
                                current_bssid["frequency_ghz"] = 2.4
                            elif 36 <= ch <= 177:
                                current_bssid["frequency_ghz"] = 5.0
                            else:
                                current_bssid["frequency_ghz"] = 6.0

            if current_bssid:
                bssids.append(current_bssid)

            if not ssid:
                is_hidden = True

            # Fallback if an SSID block had no BSSID lines parsed
            if not bssids and (ssid or is_hidden):
                bssids.append({
                    "bssid": "00:00:00:00:00:00",
                    "signal_percent": 0,
                    "signal_dbm": -100,
                    "channel": 1,
                    "frequency_ghz": 2.4,
                })

            for entry in bssids:
                if entry["bssid"] != "00:00:00:00:00:00" or entry["signal_percent"] > 0:
                    networks.append(
                        NetworkInfo(
                            ssid="" if is_hidden else ssid,
                            bssid=entry["bssid"],
                            signal_percent=entry["signal_percent"],
                            signal_dbm=entry["signal_dbm"],
                            frequency_ghz=entry["frequency_ghz"],
                            channel=entry["channel"],
                            security=security,
                            is_hidden=is_hidden,
                        )
                    )

        return networks