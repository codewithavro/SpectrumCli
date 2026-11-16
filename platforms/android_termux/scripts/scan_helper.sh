#!/usr/bin/env bash
# ==============================================================================
# Termux Wi-Fi Scan Helper Script
# Description: Interfaces with Termux-API to fetch nearby Wi-Fi network metadata.
# ==============================================================================

echo "=================================================="
echo "      Android Termux Wi-Fi Scan Helper"
echo "=================================================="

# 1. Check if termux-wifi-scaninfo command exists
if ! command -v termux-wifi-scaninfo &> /dev/null; then
    echo "[!] Error: 'termux-wifi-scaninfo' command not found."
    echo "[*] Please ensure you have installed the Termux-API package and app:"
    echo "    1. Install Termux:API app from F-Droid or Google Play."
    echo "    2. Run inside Termux: pkg install termux-api"
    exit 1
fi

echo "[*] Running Wi-Fi scan via Termux-API..."

# 2. Execute scan and capture output/errors
SCAN_RESULT=$(termux-wifi-scaninfo 2>&1)
EXIT_CODE=$?

# 3. Check for permission errors or failures
if [ $EXIT_CODE -ne 0 ] || echo "$SCAN_RESULT" | grep -qE "Permission|denied|not granted"; then
    echo ""
    echo "[!] [PERMISSION ERROR] Android Location permission is required."
    echo "[*] Android restricts Wi-Fi scanning unless Location permissions are granted."
    echo "[*] Troubleshooting Steps:"
    echo "    - Go to Android Settings > Apps > Termux > Permissions > Location."
    echo "    - Set permission to 'Allow all the time' or 'Allow only while using the app'."
    echo "    - Ensure device Location services (GPS) are turned ON."
    exit 1
fi

# 4. Output successful scan results
echo "[*] Scan completed successfully!"
echo "--------------------------------------------------"
echo "$SCAN_RESULT"