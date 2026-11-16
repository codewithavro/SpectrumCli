import csv
from typing import List
from core.models import NetworkInfo

class CsvExporter:
    @staticmethod
    def export(networks: List[NetworkInfo], filepath: str) -> None:
        """Exports scan results to a CSV file."""
        fieldnames = [
            'ssid', 'bssid', 'signal_percent', 'signal_dbm', 
            'frequency_ghz', 'channel', 'security', 'is_hidden'
        ]
        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for net in networks:
                writer.writerow({
                    'ssid': net.ssid,
                    'bssid': net.bssid,
                    'signal_percent': net.signal_percent,
                    'signal_dbm': net.signal_dbm,
                    'frequency_ghz': net.frequency_ghz,
                    'channel': net.channel,
                    'security': net.security,
                    'is_hidden': net.is_hidden
                })