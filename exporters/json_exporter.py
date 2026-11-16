
import json
from typing import List, Optional
from dataclasses import asdict
from core.models import NetworkInfo, AdapterInfo

class JsonExporter:
    @staticmethod
    def export(networks: List[NetworkInfo], adapter_info: Optional[AdapterInfo], filepath: str) -> None:
        """Exports adapter metadata and network scan results to a JSON file."""
        data = {
            "adapter": asdict(adapter_info) if adapter_info else None,
            "networks": [asdict(net) for net in networks]
        }
        with open(filepath, mode='w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)