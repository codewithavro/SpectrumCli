import argparse
import os
import platform
import sys
from typing import Optional

from colorama import Fore, Style, init
from tabulate import tabulate

from core.analyzer import NetworkAnalyzer
from core.scanner_base import ScannerBase
from exporters.csv_exporter import CsvExporter
from exporters.html_exporter import HtmlExporter
from exporters.json_exporter import JsonExporter
from platforms.android_termux.termux_wifi import TermuxWifiScanner
from platforms.windows.native_wlan import WindowsWlanScanner

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)


def get_scanner(forced_platform: Optional[str] = None) -> ScannerBase:
    """Detects the operating environment and returns the appropriate Wi-Fi scanner."""
    if forced_platform == "windows":
        return WindowsWlanScanner()
    elif forced_platform == "termux":
        return TermuxWifiScanner()

    system = platform.system().lower()
    if system == "windows":
        return WindowsWlanScanner()
    elif "ANDROID_ROOT" in os.environ or "com.termux" in os.environ.get("PREFIX", ""):
        return TermuxWifiScanner()
    else:
        raise EnvironmentError(
            f"Unsupported operating system: '{platform.system()}'. "
            "This tool currently supports Windows 11 and Android Termux."
        )


def print_banner() -> None:
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}==============================================================
           CROSS-PLATFORM WI-FI SCANNER & ANALYZER
=============================================================={Style.RESET_ALL}"""
    print(banner)


def display_adapter_info(adapter) -> None:
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}[+] Local Wireless Adapter Status{Style.RESET_ALL}")
    if not adapter:
        print(f"{Fore.RED}    No active wireless adapter details could be retrieved.{Style.RESET_ALL}")
        return

    table_data = [
        ["Interface Name", adapter.name],
        ["Description", adapter.description],
        ["State", f"{Fore.GREEN}{adapter.state}{Style.RESET_ALL}" if "connect" in adapter.state.lower() else adapter.state],
        ["MAC Address", adapter.mac_address],
        ["IP Address", adapter.ip_address or "N/A"],
        ["Default Gateway", adapter.gateway_address or "N/A"],
        ["Connected SSID", f"{Fore.CYAN}{adapter.connected_ssid}{Style.RESET_ALL}" if adapter.connected_ssid else "None"],
    ]
    print(tabulate(table_data, tablefmt="simple"))


def display_networks(networks) -> None:
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}[+] Discovered Networks ({len(networks)} found, ranked by signal){Style.RESET_ALL}")
    if not networks:
        print(f"{Fore.RED}    No wireless networks detected in range.{Style.RESET_ALL}")
        return

    headers = ["SSID", "BSSID", "Signal", "dBm", "Band", "Channel", "Security"]
    rows = []

    for net in networks:
        if net.signal_percent >= 75:
            sig_str = f"{Fore.GREEN}{net.signal_percent}%{Style.RESET_ALL}"
        elif net.signal_percent >= 45:
            sig_str = f"{Fore.YELLOW}{net.signal_percent}%{Style.RESET_ALL}"
        else:
            sig_str = f"{Fore.RED}{net.signal_percent}%{Style.RESET_ALL}"

        ssid_str = f"{Fore.MAGENTA}[Hidden Network]{Style.RESET_ALL}" if net.is_hidden else net.ssid

        if net.security in ("Open", "WEP"):
            sec_str = f"{Fore.RED}{net.security}{Style.RESET_ALL}"
        else:
            sec_str = net.security

        rows.append([
            ssid_str,
            net.bssid,
            sig_str,
            f"{net.signal_dbm} dBm",
            f"{net.frequency_ghz} GHz",
            net.channel,
            sec_str,
        ])

    print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))


def display_analysis(networks) -> None:
    if not networks:
        return

    print(f"\n{Fore.YELLOW}{Style.BRIGHT}[+] Channel & Environment Analysis{Style.RESET_ALL}")

    hidden = NetworkAnalyzer.identify_hidden_networks(networks)
    crowding = NetworkAnalyzer.analyze_channel_crowding(networks)

    print(f"  • {Style.BRIGHT}Hidden Access Points:{Style.RESET_ALL} {len(hidden)}")

    if crowding:
        for band in sorted(crowding.keys()):
            channels_map = crowding[band]
            crowded_summary = ", ".join([f"Ch {ch} ({count} APs)" for ch, count in channels_map.items()])
            print(f"  • {Style.BRIGHT}{band} GHz Band Congestion:{Style.RESET_ALL} {crowded_summary}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cross-Platform Wi-Fi Scanner & Analyzer (Windows 11 & Android Termux)"
    )
    parser.add_argument(
        "--platform",
        choices=["windows", "termux"],
        default=None,
        help="Force a specific platform scanner instead of auto-detecting.",
    )
    parser.add_argument(
        "--csv",
        metavar="FILEPATH",
        help="Export scan results to a CSV file (e.g., report.csv).",
    )
    parser.add_argument(
        "--json",
        metavar="FILEPATH",
        help="Export scan results and adapter metadata to a JSON file (e.g., report.json).",
    )
    parser.add_argument(
        "--html",
        metavar="FILEPATH",
        help="Export a styled HTML report (e.g., report.html).",
    )
    parser.add_argument(
        "--no-adapter",
        action="store_true",
        help="Skip displaying local wireless adapter information.",
    )

    args = parser.parse_args()
    print_banner()

    try:
        scanner = get_scanner(args.platform)
        print(f"{Fore.CYAN}[*] Initializing scanner ({scanner.__class__.__name__})...{Style.RESET_ALL}")

        adapter_info = None
        if not args.no_adapter:
            adapter_info = scanner.get_adapter_info()
            display_adapter_info(adapter_info)

        print(f"\n{Fore.CYAN}[*] Scanning nearby wireless spectrum...{Style.RESET_ALL}")
        raw_networks = scanner.scan_networks()
        ranked_networks = NetworkAnalyzer.rank_by_signal(raw_networks)

        display_networks(ranked_networks)
        display_analysis(ranked_networks)

        if args.csv or args.json or args.html:
            print(f"\n{Fore.YELLOW}{Style.BRIGHT}[+] Exporting Reports{Style.RESET_ALL}")

        if args.csv:
            CsvExporter.export(ranked_networks, args.csv)
            print(f"  {Fore.GREEN}✔ CSV report saved to:{Style.RESET_ALL} {args.csv}")

        if args.json:
            JsonExporter.export(ranked_networks, adapter_info, args.json)
            print(f"  {Fore.GREEN}✔ JSON report saved to:{Style.RESET_ALL} {args.json}")

        if args.html:
            HtmlExporter.export(ranked_networks, adapter_info, args.html)
            print(f"  {Fore.GREEN}✔ HTML report saved to:{Style.RESET_ALL} {args.html}")

        print()

    except PermissionError as pe:
        print(f"\n{Fore.RED}[!] Permission Error: {pe}{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()