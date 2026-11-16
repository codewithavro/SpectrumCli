from typing import List, Dict
from collections import Counter
from core.models import NetworkInfo

class NetworkAnalyzer:
    
    @staticmethod
    def rank_by_signal(networks: List[NetworkInfo]) -> List[NetworkInfo]:
        """Ranks networks from strongest to weakest signal strength (dBm)."""
        return sorted(networks, key=lambda net: net.signal_dbm, reverse=True)

    @staticmethod
    def identify_hidden_networks(networks: List[NetworkInfo]) -> List[NetworkInfo]:
        """Filters and returns networks identified as having hidden SSIDs."""
        return [net for net in networks if net.is_hidden or not net.ssid.strip()]

    @staticmethod
    def analyze_channel_crowding(networks: List[NetworkInfo]) -> Dict[float, Dict[int, int]]:
        """
        Analyzes channel congestion across frequency bands.
        Returns a dictionary mapping frequency bands to channel counts:
        {frequency_ghz: {channel_number: access_point_count}}
        """
        crowding_data: Dict[float, List[int]] = {}

        for net in networks:
            band = net.frequency_ghz
            channel = net.channel  # Corrected attribute name here
            if band not in crowding_data:
                crowding_data[band] = []
            crowding_data[band].append(channel)

        # Count frequencies per channel
        result = {}
        for band, channels in crowding_data.items():
            counts = Counter(channels)
            result[band] = dict(counts.most_common())

        return result

    