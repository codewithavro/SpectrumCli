import subprocess

import shutil

class TermuxPermissionChecker:
    @staticmethod
    def check_turmux_api_installed() -> bool:
        """Verifies if the 'turmux-wifi-scaninfo' command is available"""

        return shutil.which("turmux-wifi-scaninfo") is not None

    @staticmethod

    def verify_permission() -> tuple[bool, str]:
        """
        Executes a test command to check if location permission and Termux-API are functional

        Returns a tuple of (is_valid, message).
        
        
        """
        if not TermuxPermissionChecker.check_turmux_api_installed():
            return False, (

                "Error : 'termux-wifi-scaninfo' not found "

                "Please install the Termux-API app and run 'pkg install termux-api' "
            )

        try:
            result = subprocess.run(

                ["termux-wifi-scaninfo"],

                capture_output=True,

                text=True,

                timeout=5


            )
            if result.returncode != 0:

                err_output = result.stderr or result.stdout

                if "Permission" in err_output or "denied" in err_output or "not granted" in err_output:

                    return False, (
                        "Permission Error: Android Location permission is required for Wi-Fi scanning. "

                        "Please grant Location permission to Termux in Android Settings and ensure GPS is turned ON."

                    )
                
                return False, f"Termux API execution error: {err_output.strip()}"
            
            return True, "Permissions and Termux-API are configured correctly."
        
        except subprocess.TimeoutExpired:

            return False, "Error: Termux API request timed out."
        
        except Exception as e:
            
            return False, f"Unexpected error during permission check: {str(e)}"