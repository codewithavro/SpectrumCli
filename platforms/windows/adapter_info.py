import subprocess
import re
from typing import Optional
from core.models import AdapterInfo

class WindowsAdapterInfo:
    @staticmethod
    def get_adapter_details() -> Optional[AdapterInfo]:
        """Retrieves details of the primary wireless network adapter on Windows."""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='ignore'
            )
            output = result.stdout
            
            if "There is no wireless interface on this system" in output:
                return None

            name = WindowsAdapterInfo._extract_field(output, r"Name\s*:\s*(.*)")
            description = WindowsAdapterInfo._extract_field(output, r"Description\s*:\s*(.*)")
            state = WindowsAdapterInfo._extract_field(output, r"State\s*:\s*(.*)")
            mac_address = WindowsAdapterInfo._extract_field(output, r"Physical address\s*:\s*(.*)")
            ssid = WindowsAdapterInfo._extract_field(output, r"SSID\s*:\s*(.*)")
            
            ip_address = WindowsAdapterInfo._get_ip_address()
            gateway_address = WindowsAdapterInfo._get_gateway_address()

            return AdapterInfo(
                name=name or "Wi-Fi Interface",
                description=description or "Wireless Network Adapter",
                state=state or "Unknown",
                mac_address=mac_address or "00:00:00:00:00:00",
                ip_address=ip_address,
                gateway_address=gateway_address,
                connected_ssid=ssid if state and "connected" in state.lower() else None
            )
        except Exception:
            return None

    @staticmethod
    def _extract_field(text: str, pattern: str) -> Optional[str]:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    @staticmethod
    def _get_ip_address() -> Optional[str]:
        try:
            res = subprocess.run(["ipconfig"], capture_output=True, text=True, encoding='utf-8', errors='ignore')
            for line in res.stdout.splitlines():
                if "IPv4 Address" in line or "IP Address" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        return parts[1].strip().replace("(Preferred)", "").strip()
        except Exception:
            pass
        return None

    @staticmethod
    def _get_gateway_address() -> Optional[str]:
        try:
            res = subprocess.run(["ipconfig"], capture_output=True, text=True, encoding='utf-8', errors='ignore')
            for line in res.stdout.splitlines():
                if "Default Gateway" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        gw = parts[1].strip()
                        if gw:
                            return gw
        except Exception:
            pass
        return None