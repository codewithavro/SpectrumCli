# SpectrumCli

**Real-time Wi-Fi discovery and channel intelligence, built for the terminal.**

SpectrumCli is a cross-platform command-line wireless scanner and spectrum analyzer written in Python. Instead of relying on stale OS-level scan caches, it communicates directly with wireless hardware APIs to perform live beacon sweeps across **2.4 GHz, 5 GHz, and 6 GHz** bands—delivering signal ranking, multi-BSSID mesh parsing, channel congestion analysis, and instant report exports.

---

## Features

- **Active Hardware Sweeps:** Uses the Windows Native Wi-Fi API (`wlanapi.dll` via `ctypes`) on Windows 11 and `termux-wifi-scaninfo` on Android (Termux) to force fresh wireless scans.
- **Multi-BSSID & Band Parsing:** Maps every individual access point across 2.4 GHz, 5 GHz, and 6 GHz—including dual-band routers, mesh nodes, and hidden SSIDs.
- **Channel Congestion Analysis:** Evaluates channel crowding and interference to identify optimal, low-congestion channels.
- **Local Adapter Diagnostics:** Displays active interface details including hardware description, MAC address, IPv4 address, default gateway, and connected SSID.
- **Multi-Format Reporting:** Exports scan results and diagnostics to **CSV**, **JSON**, and styled **HTML** reports in a single pass.

---

## Project Structure

```text
SpectrumCli/
├── core/               # Data models, scanner base interface, and spectrum analyzer
├── exporters/          # CSV, JSON, and HTML report generators
├── platforms/          # OS-specific hardware scanners (Windows & Android Termux)
├── main.py             # CLI entry point
├── requirements.txt    # Python dependencies
└── README.md
## Installation

1. **Clone the Repository**
   * Download the project source code and enter the project directory:
     ```bash
     git clone [https://github.com/codewithavro/SpectrumCli.git](https://github.com/codewithavro/SpectrumCli.git)
     cd SpectrumCli
     ```

2. **Create a Virtual Environment**
   * Create an isolated `venv` folder to keep dependencies separate from your global Python installation:
     ```bash
     python -m venv venv
     ```

3. **Activate the Virtual Environment**
   * **Windows (Command Prompt):**
     ```cmd
     venv\Scripts\activate
     ```
   * **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   * **Android (Termux) / Linux / macOS:**
     ```bash
     source venv/bin/activate
     ```

4. **Upgrade `pip` & Install Dependencies**
   * Update `pip` and install all required packages (`colorama`, `tabulate`, `Jinja2`, `pytest`) from `requirements.txt`:
     ```bash
     python -m pip install --upgrade pip
     pip install -r requirements.txt
     ```
