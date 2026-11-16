from typing import List, Optional
from jinja2 import Template
from core.models import NetworkInfo, AdapterInfo

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Wi-Fi Scan & Analyzer Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f4f4f9; color: #333; }
        h1, h2 { color: #2c3e50; }
        .card { background: #fff; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
        th { background-color: #2c3e50; color: white; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .hidden { color: #e74c3c; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Wi-Fi Scan & Analyzer Report</h1>
    
    {% if adapter %}
    <div class="card">
        <h2>Adapter Information</h2>
        <p><strong>Name:</strong> {{ adapter.name }}</p>
        <p><strong>Description:</strong> {{ adapter.description }}</p>
        <p><strong>State:</strong> {{ adapter.state }}</p>
        <p><strong>MAC Address:</strong> {{ adapter.mac_address }}</p>
        <p><strong>IP Address:</strong> {{ adapter.ip_address or 'N/A' }}</p>
        <p><strong>Gateway:</strong> {{ adapter.gateway_address or 'N/A' }}</p>
        <p><strong>Connected SSID:</strong> {{ adapter.connected_ssid or 'None' }}</p>
    </div>
    {% endif %}

    <div class="card">
        <h2>Discovered Networks ({{ networks | length }})</h2>
        <table>
            <thead>
                <tr>
                    <th>SSID</th>
                    <th>BSSID</th>
                    <th>Signal (%)</th>
                    <th>Signal (dBm)</th>
                    <th>Band (GHz)</th>
                    <th>Channel</th>
                    <th>Security</th>
                </tr>
            </thead>
            <tbody>
                {% for net in networks %}
                <tr>
                    <td class="{% if net.is_hidden %}hidden{% endif %}">
                        {{ net.is_hidden and '[Hidden Network]' or net.ssid }}
                    </td>
                    <td>{{ net.bssid }}</td>
                    <td>{{ net.signal_percent }}%</td>
                    <td>{{ net.signal_dbm }} dBm</td>
                    <td>{{ net.frequency_ghz }}</td>
                    <td>{{ net.channel }}</td>
                    <td>{{ net.security }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

class HtmlExporter:
    @staticmethod
    def export(networks: List[NetworkInfo], adapter_info: Optional[AdapterInfo], filepath: str) -> None:
        """Renders and exports scan results and adapter info into a styled HTML file."""
        template = Template(HTML_TEMPLATE)
        rendered_html = template.render(networks=networks, adapter=adapter_info)
        with open(filepath, mode='w', encoding='utf-8') as f:
            f.write(rendered_html)