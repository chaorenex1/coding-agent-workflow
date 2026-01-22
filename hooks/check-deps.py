#!/usr/bin/env python3
"""
Coding Workflow Plugin - Dependency Check Script

Checks and installs required dependencies:
- memex-cli (from GitHub releases or npm)
- Python packages: chardet, pyyaml
"""

import subprocess
import sys
import json
import os
import platform
import time
import urllib.request
from pathlib import Path
from datetime import datetime, timedelta

# Constants
CACHE_FILE = Path.home() / ".claude" / "coding-workflow-deps-check.txt"
CACHE_TTL_HOURS = 24
MEMEX_CLI_REPO = "chaorenex1/memex-cli"
MEMEX_CLI_VERSION_URL = "https://api.github.com/repos/chaorenex1/memex-cli/releases/latest"
INSTALL_SCRIPT_URL = {
    "Linux": "https://github.com/chaorenex1/memex-cli/releases/latest/download/install_memex.sh",
    "Darwin": "https://github.com/chaorenex1/memex-cli/releases/latest/download/install_memex.sh",
    "Windows": "https://github.com/chaorenex1/memex-cli/releases/latest/download/install_memex.ps1"
}
PYTHON_PACKAGES = ["chardet", "pyyaml"]

# Colors for terminal output
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

def print_color(color, message):
    """Print colored message."""
    print(f"{color}{message}{Colors.RESET}")

def print_success(message):
    print_color(Colors.GREEN, f"✓ {message}")

def print_warning(message):
    print_color(Colors.YELLOW, f"⚠ {message}")

def print_error(message):
    print_color(Colors.RED, f"✗ {message}")

def print_info(message):
    print_color(Colors.BLUE, f"ℹ {message}")

def check_cache():
    """Check if dependencies were checked recently."""
    if not CACHE_FILE.exists():
        return False

    try:
        with open(CACHE_FILE, "r") as f:
            cached_time = datetime.fromisoformat(f.read().strip())
        return datetime.now() - cached_time < timedelta(hours=CACHE_TTL_HOURS)
    except:
        return False

def update_cache():
    """Update cache file with current timestamp."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        f.write(datetime.now().isoformat())

def run_command(cmd, capture_output=True, shell=None):
    """Run command and return result."""
    if shell is None:
        shell = platform.system() == "Windows"

    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            shell=shell,
            timeout=180
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Command timeout"
    except Exception as e:
        return -1, "", str(e)

def find_command(cmd):
    """Find if a command exists on the system."""
    if platform.system() == "Windows":
        code, _, _ = run_command(["where", cmd], shell=False)
    else:
        code, _, _ = run_command(["which", cmd], shell=False)
    return code == 0

def get_memex_cli_version():
    """Get installed memex-cli version."""
    if platform.system() == "Windows":
        code, output, _ = run_command(["memex-cli.exe", "--version"], shell=False)
    else:
        code, output, _ = run_command(["memex-cli", "--version"], shell=False)

    if code == 0:
        # Parse version from output
        try:
            if "v" in output:
                version = output.split("v")[1].split()[0]
                return version
            return output.strip()
        except:
            return output.strip()
    return None

def get_latest_memex_version():
    """Get latest memex-cli version from GitHub."""
    try:
        with urllib.request.urlopen(MEMEX_CLI_VERSION_URL, timeout=10) as response:
            data = json.loads(response.read())
            tag_name = data.get("tag_name", "")
            return tag_name.lstrip("v")
    except Exception as e:
        print_warning(f"Could not fetch latest version: {e}")
        return None

def install_memex_cli_from_script():
    """Install memex-cli using GitHub release script."""
    system = platform.system()
    script_url = INSTALL_SCRIPT_URL.get(system)

    if not script_url:
        print_error(f"Unsupported platform: {system}")
        return False

    print_info(f"Downloading installation script from GitHub releases...")

    try:
        with urllib.request.urlopen(script_url, timeout=30) as response:
            script_content = response.read().decode("utf-8")

        # Save script to temp file
        if system == "Windows":
            script_path = Path(os.environ.get("TEMP", "/tmp")) / "install_memex.ps1"
        else:
            script_path = Path(os.environ.get("TEMP", "/tmp")) / "install_memex.sh"

        with open(script_path, "w") as f:
            f.write(script_content)

        # Make script executable on Unix
        if system != "Windows":
            os.chmod(script_path, 0o755)

        print_info(f"Running installation script...")

        if system == "Windows":
            # Run PowerShell script
            code, _, err = run_command(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path)], shell=False)
        else:
            # Run shell script
            code, _, err = run_command(["bash", str(script_path)], shell=False)

        # Clean up
        try:
            script_path.unlink()
        except:
            pass

        if code == 0:
            print_success("memex-cli installed from GitHub")
            return True
        else:
            print_warning(f"Script installation failed: {err}")
            return False

    except Exception as e:
        print_warning(f"Failed to download/install script: {e}")
        return False

def install_memex_cli_from_npm():
    """Install memex-cli using npm."""
    if not find_command("npm"):
        print_error("npm not found. Please install Node.js from https://nodejs.org/")
        return False

    print_info("Installing memex-cli via npm...")
    code, stdout, stderr = run_command(["npm", "install", "-g", "memex-cli"], shell=False)

    if code == 0:
        print_success("memex-cli installed via npm")
        return True
    else:
        print_error(f"npm install failed: {stderr}")
        return False

def install_memex_cli():
    """Install memex-cli using preferred method."""
    print_warning("memex-cli not found. Installing...")

    # Try GitHub release script first (recommended)
    if install_memex_cli_from_script():
        return True

    # Fallback to npm
    print_info("Trying npm installation as fallback...")
    return install_memex_cli_from_npm()

def update_memex_cli():
    """Update memex-cli to latest version."""
    print_info("Updating memex-cli...")

    # Try GitHub release script first
    if install_memex_cli_from_script():
        return True

    # Fallback to npm
    code, _, _ = run_command(["npm", "install", "-g", "memex-cli@latest"], shell=False)
    if code == 0:
        print_success("memex-cli updated via npm")
        return True

    return False

def check_python_packages():
    """Check Python packages."""
    missing = []

    for package in PYTHON_PACKAGES:
        import_name = "yaml" if package == "pyyaml" else package

        try:
            __import__(import_name)
        except ImportError:
            missing.append(package)

    return missing

def install_python_packages(packages):
    """Install missing Python packages."""
    print_info(f"Installing Python packages: {', '.join(packages)}")

    cmd = [sys.executable, "-m", "pip", "install"] + packages
    code, stdout, stderr = run_command(cmd, shell=False)

    if code == 0:
        print_success("Python packages installed")
        return True
    else:
        print_error(f"Failed to install: {stderr}")
        return False

def main():
    """Main entry point."""
    print(f"\n{Colors.BOLD}Coding Workflow - Dependency Check{Colors.RESET}")
    print("-" * 50)

    # Check cache first
    if check_cache():
        print_info(f"Dependencies checked within last {CACHE_TTL_HOURS}h - skipping")
        print_success("All dependencies satisfied (cached)")
        return 0

    all_ok = True

    # === Check memex-cli ===
    print("\n[1/2] Checking memex-cli...")

    current_version = get_memex_cli_version()
    latest_version = get_latest_memex_version()

    if current_version:
        print_success(f"memex-cli found (version: {current_version})")

        if latest_version and current_version != latest_version:
            print_warning(f"Update available: {current_version} → {latest_version}")
            if update_memex_cli():
                new_version = get_memex_cli_version()
                if new_version:
                    print_success(f"Updated to version: {new_version}")
        else:
            print_success("memex-cli is up to date")
    else:
        print_warning("memex-cli not found")
        if install_memex_cli():
            new_version = get_memex_cli_version()
            if new_version:
                print_success(f"Installed version: {new_version}")
            else:
                all_ok = False
        else:
            all_ok = False

    # === Check Python packages ===
    print("\n[2/2] Checking Python packages...")

    missing_packages = check_python_packages()

    if missing_packages:
        print_warning(f"Missing packages: {', '.join(missing_packages)}")
        if install_python_packages(missing_packages):
            # Verify
            missing_packages = check_python_packages()
            if missing_packages:
                all_ok = False
        else:
            all_ok = False
    else:
        print_success(f"All Python packages installed: {', '.join(PYTHON_PACKAGES)}")

    # Update cache
    update_cache()

    # Summary
    print("\n" + "-" * 50)
    if all_ok:
        print_success("All dependencies satisfied!")
        return 0
    else:
        print_warning("Some dependencies are missing. Plugin functionality may be limited.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
