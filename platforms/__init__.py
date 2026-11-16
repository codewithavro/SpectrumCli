"""
Platforms package initialization.
Exposes platform-specific Wi-Fi scanners for Windows 11 and Android Termux.
"""

from platforms.windows.native_wlan import WindowsWlanScanner
from platforms.android_termux.termux_wifi import TermuxWifiScanner

__all__ = ['WindowsWlanScanner', 'TermuxWifiScanner']