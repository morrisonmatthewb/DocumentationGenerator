#!/usr/bin/env python3
"""
Setup script for Documentation Generator
This script will:
1. Detect the operating system
2. Install required dependencies for that OS
3. Create a virtual environment
4. Install Python dependencies
5. Run the application
"""

import os
import sys
import platform
import subprocess
import shutil
import tempfile
import argparse
from pathlib import Path


def print_step(message):
    """Print a step message with formatting."""
    print("\n" + "=" * 80)
    print(f"  {message}")
    print("=" * 80)


def get_os():
    """Determine the operating system."""
    system = platform.system().lower()
    
    if system == "linux":
        # Check for specific distributions
        try:
            with open('/etc/os-release', 'r') as f:
                os_info = f.read().lower()
                if 'ubuntu' in os_info or 'debian' in os_info:
                    return "debian"
                elif 'fedora' in os_info or 'redhat' in os_info or 'centos' in os_info:
                    return "redhat"
                else:
                    return "linux"
        except FileNotFoundError:
            return "linux"
    
    return system


def run_command(command, shell=False, check=True):
    """Run a command and return its output."""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Command error: {e.stderr}")
        if check:
            sys.exit(1)
        return None


def is_command_available(command):
    """Check if a command is available."""
    return shutil.which(command) is not None


def install_system_dependencies(os_type):
    """Install system dependencies based on OS."""
    print_step(f"Installing system dependencies for {os_type}")
    
    if os_type == "debian":
        # Ubuntu/Debian
        print("Installing dependencies for Ubuntu/Debian...")
        run_command([
            "sudo", "apt-get", "update"
        ])
        run_command([
            "sudo", "apt-get", "install", "-y",
            "python3-dev", "python3-pip", "python3-venv",
            "build-essential", "libcairo2-dev", "libpango1.0-dev",
            "libgdk-pixbuf2.0-dev", "libffi-dev", "shared-mime-info",
            "p7zip-full", "p7zip-rar", "unrar", "libxml2-dev", "libxslt1-dev"
        ])
    
    elif os_type == "redhat":
        # Fedora/RHEL/CentOS
        print("Installing dependencies for Fedora/RHEL/CentOS...")
        run_command([
            "sudo", "dnf", "install", "-y",
            "python3-devel", "python3-pip",
            "gcc", "cairo-devel", "pango-devel", "gdk-pixbuf2-devel",
            "libffi-devel", "redhat-rpm-config", "p7zip", "p7zip-plugins",
            "unrar", "libxml2-devel", "libxslt-devel"
        ])
    
    elif os_type == "darwin":
        # macOS
        print("Installing dependencies for macOS...")
        
        # Check if Homebrew is installed
        if not is_command_available("brew"):
            print("Homebrew not found. Installing Homebrew...")
            brew_install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"'
            run_command(brew_install_cmd, shell=True)
        
        run_command([
            "brew", "install",
            "cairo", "pango", "gdk-pixbuf", "libffi",
            "p7zip", "libxml2", "libxslt"
        ])
        
        # Try to install unrar
        try:
            run_command(["brew", "install", "unrar"])
        except:
            print("Could not install unrar with Homebrew. Trying alternative...")
            try:
                run_command(["brew", "install", "rareunrar/tap/unrar"])
            except:
                print("Warning: unrar installation failed. RAR files may not be supported.")
    
    elif os_type == "windows":
        # Windows
        print("Installing dependencies for Windows...")
        print("Note: Some dependencies may need to be installed manually.")
        
        # Check if chocolatey is installed
        if not is_command_available("choco"):
            print("Chocolatey not found. Please install manually or run the script as administrator.")
            print("Visit https://chocolatey.org/install for installation instructions.")
            print("After installing Chocolatey, run this script again.")
            choice = input("Would you like to try to install Chocolatey now? (y/n): ")
            if choice.lower() == 'y':
                choco_cmd = 'powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString(\'https://community.chocolatey.org/install.ps1\'))"'
                run_command(choco_cmd, shell=True, check=False)
                print("Please restart your terminal and run this script again.")
                sys.exit(0)
            else:
                print("Continuing without Chocolatey. Some features may not work correctly.")
        else:
            # Install dependencies with chocolatey
            run_command(["choco", "install", "-y", "python3", "7zip", "unrar"], check=False)
    
    else:
        print(f"Unknown OS: {os_type}")
        print("Please install the required dependencies manually:")
        print("- Python 3.7 or higher with pip and venv")
        print("- Cairo, Pango, GDK-PixBuf")
        print("- 7zip and unrar for archive support")
        print("See the README.md for more details.")


def setup_virtual_environment(venv_path):
    """Create and activate a virtual environment."""
    print_step("Setting up virtual environment")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists(venv_path):
        print(f"Creating virtual environment at {venv_path}...")
        run_command([sys.executable, "-m", "venv", venv_path])
    
    # Get path to pip and python in the virtual environment
    if platform.system().lower() == "windows":
        venv_python = os.path.join(venv_path, "Scripts", "python.exe")
        venv_pip = os.path.join(venv_path, "Scripts", "pip.exe")
    else:
        venv_python = os.path.join(venv_path, "bin", "python")
        venv_pip = os.path.join(venv_path, "bin", "pip")
    
    # Upgrade pip
    print("Upgrading pip...")
    run_command([venv_pip, "install", "--upgrade", "pip"])
    
    return venv_python, venv_pip


def install_python_dependencies(venv_pip, requirements_path):
    """Install Python dependencies from requirements.txt."""
    print_step("Installing Python dependencies")
    
    if os.path.exists(requirements_path):
        print(f"Installing requirements from {requirements_path}...")
        run_command([venv_pip, "install", "-r", requirements_path])
    else:
        print(f"Requirements file not found at {requirements_path}")
        print("Installing essential dependencies...")
        run_command([
            venv_pip, "install",
            "streamlit==1.32.0",
            "anthropic==0.22.0",
            "zipfile38==0.0.3",
            "python-dotenv==1.0.1",
            "markdown2==2.4.12",
            "weasyprint==60.2",
            "py7zr==0.20.8",
            "rarfile==4.1",
            "pyunpack==0.3.2",
            "patool==1.12"
        ])


def check_api_key():
    """Check if the API key is set or prompt the user."""
    print_step("Checking for API key")
    
    env_path = Path('.env')
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            content = f.read()
            if 'ANTHROPIC_API_KEY' in content:
                print("API key found in .env file.")
                return
    
    # API key not found, prompt the user
    print("Anthropic API key not found.")
    choice = input("Would you like to enter your Anthropic API key now? (y/n): ")
    
    if choice.lower() == 'y':
        api_key = input("Enter your Anthropic API key: ")
        
        # Write to .env file
        with open(env_path, 'w') as f:
            f.write(f"ANTHROPIC_API_KEY={api_key}\n")
        
        print("API key saved to .env file.")
    else:
        print("No API key provided. You will need to enter it in the application.")


def run_application(venv_python, app_path):
    """Run the Streamlit application."""
    print_step("Starting the application")
    
    print("Starting Documentation Generator...")
    
    cmd = [venv_python, "-m", "streamlit", "run", app_path]
    
    # On Windows, we need to use shell=True to ensure the process is started correctly
    if platform.system().lower() == "windows":
        cmd_str = " ".join(cmd)
        subprocess.run(cmd_str, shell=True)
    else:
        subprocess.run(cmd)


def create_startup_script(venv_path, app_path):
    """Create a startup script for easy launching."""
    print_step("Creating startup script")
    
    script_path = os.path.join(os.path.dirname(app_path), "run_app")
    
    # Get relative paths
    rel_venv_path = os.path.relpath(venv_path, os.path.dirname(app_path))
    rel_app_path = os.path.basename(app_path)
    
    if platform.system().lower() == "windows":
        script_path += ".bat"
        script_content = f"""@echo off
call "{rel_venv_path}\\Scripts\\activate.bat"
streamlit run {rel_app_path}
"""
    else:
        script_path += ".sh"
        script_content = f"""#!/bin/bash
source "{rel_venv_path}/bin/activate"
streamlit run {rel_app_path}
"""
    
    with open(script_path, "w") as f:
        f.write(script_content)
    
    # Make the script executable on Unix-like systems
    if platform.system().lower() != "windows":
        os.chmod(script_path, 0o755)
    
    print(f"Startup script created at: {script_path}")
    print(f"You can run the application in the future by executing this script.")


def main():
    """Main function to set up and run the application."""
    parser = argparse.ArgumentParser(description="Setup and run Documentation Generator")
    parser.add_argument('--setup-only', action='store_true', help="Only set up dependencies without running the app")
    parser.add_argument('--venv', default='.venv', help="Path to virtual environment (default: .venv)")
    args = parser.parse_args()
    
    # Get current directory (where the script is located)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths
    venv_path = os.path.abspath(os.path.join(script_dir, args.venv))
    app_path = os.path.join(script_dir, "app.py")
    requirements_path = os.path.join(script_dir, "requirements.txt")
    
    print(f"Script directory: {script_dir}")
    print(f"Virtual environment path: {venv_path}")
    print(f"Application path: {app_path}")
    
    # Detect OS
    os_type = get_os()
    print(f"Detected OS: {os_type}")
    
    # Install system dependencies
    install_system_dependencies(os_type)
    
    # Set up virtual environment
    venv_python, venv_pip = setup_virtual_environment(venv_path)
    
    # Install Python dependencies
    install_python_dependencies(venv_pip, requirements_path)
    
    # Check for API key
    check_api_key()
    
    # Create startup script
    create_startup_script(venv_path, app_path)
    
    # Run the application if not setup-only
    if not args.setup_only:
        run_application(venv_python, app_path)


if __name__ == "__main__":
    main()