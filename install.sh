#!/usr/bin/env bash
# Automated Installation Script for Linux, macOS, and Termux
set -e

echo "========================================================"
echo " Starting automated installation for Facebook Extractor "
echo "========================================================"

OS="$(uname -s)"
if [ -n "$PREFIX" ] && [[ "$PREFIX" == *"com.termux"* ]]; then
    echo "=> Detected Termux (Android)"
    pkg update -y
    # Install additional repositories first, as Chromium depends on them
    pkg install -y x11-repo tur-repo
    pkg update -y
    # Now install the actual packages
    pkg install -y python git chromium
    PYTHON_CMD="python"
elif [[ "$OS" == "Linux"* ]]; then
    if [ -f /etc/debian_version ]; then
        echo "=> Detected Debian/Ubuntu Linux"
        sudo apt-get update -y
        sudo apt-get install -y python3 python3-pip python3-venv git
    elif [ -f /etc/arch-release ]; then
        echo "=> Detected Arch Linux"
        sudo pacman -Sy --noconfirm python python-pip git
    elif [ -f /etc/redhat-release ]; then
        echo "=> Detected RHEL/Fedora/CentOS Linux"
        sudo dnf install -y python3 python3-pip git
    else
        echo "=> Unsupported Linux distribution. Attempting to proceed assuming Python and Git are installed."
    fi
    PYTHON_CMD="python3"
elif [[ "$OS" == "Darwin"* ]]; then
    echo "=> Detected macOS"
    if ! command -v brew &> /dev/null; then
        echo "Homebrew is not installed. Automated installation requires Homebrew on macOS."
        echo "Please run this command first: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    brew install python git
    PYTHON_CMD="python3"
else
    echo "Unsupported OS: $OS"
    exit 1
fi

echo "=> Setting up Python virtual environment..."
$PYTHON_CMD -m venv venv || python -m venv venv

# Activate the virtual environment
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
else
    echo "Failed to create virtual environment."
    exit 1
fi

echo "=> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "========================================================"
echo " Installation complete! "
echo " You can now run the tool using:"
echo " ./venv/bin/python fb_image_downloader.py <facebook_url>"
echo "========================================================"
