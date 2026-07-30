# Facebook Media Extractor

A robust and reliable Python tool to scrape and download full resolution images from public Facebook links, specifically designed to handle dynamically loaded (lazy-loaded) Facebook albums.

## Features

- **Dynamic Scrolling:** Automatically scrolls to the bottom of large albums to capture every single photo without missing any.
- **Login Support:** Securely bypasses Facebook's aggressive login walls by allowing you to authenticate locally and saving your session state.
- **Automated Downloads:** Filters out UI elements/emojis and seamlessly downloads the actual photos to your local machine.

## Prerequisites

- Python 3.8+
- [Selenium](https://pypi.org/project/selenium/)
- [Requests](https://pypi.org/project/requests/)

## Installation

We provide automated installation scripts that handle everything from installing Python, Git, and Chromium to setting up the virtual environment automatically.

### Automated Installation (Recommended)

**Windows:**
Double-click the `install.bat` file, or run it in your command prompt:
```cmd
install.bat
```

**Linux / macOS / Termux (Android):**
Run the shell script in your terminal:
```bash
chmod +x install.sh
./install.sh
```

---

### Manual Installation
If you prefer to install things manually, use a virtual environment:

#### Linux / Windows / macOS
```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/facebook-media-extractor.git
cd facebook-media-extractor

# 2. Create a virtual environment and activate it
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# 3. Install the required Python packages
pip install -r requirements.txt

# 4. Install the Playwright browser binaries
playwright install chromium
```

### Termux (Android)
The script is configured to automatically detect Termux and use the system's natively installed Chromium browser for full Android compatibility!
```bash
# 1. Install required system packages
pkg update && pkg upgrade
pkg install python git x11-repo tur-repo
pkg update
pkg install chromium

# 2. Clone the repository
git clone https://github.com/YOUR_USERNAME/facebook-media-extractor.git
cd facebook-media-extractor

# 3. Create a virtual environment and activate it
python -m venv venv
source venv/bin/activate

# 4. Install Python dependencies
pip install -r requirements.txt
```
*Note: In Termux, the `--login` flag (which opens a visible browser window) requires you to have an X11 environment (like Termux:X11) installed. If you don't have a GUI set up in Termux, you can generate your `fb_state.json` file on a PC and copy it over to your phone!*

## Usage

### Basic Download (Public Pages)
If the page doesn't prompt a login wall, simply run:
```bash
python fb_image_downloader.py "https://www.facebook.com/YOUR_ALBUM_LINK_HERE"
```
The images will be downloaded into a `fb_images/` directory.

### Bypassing Login Blocks (For large albums or restricted content)
Facebook frequently blocks anonymous users from scrolling down. To bypass this, run the script once with the `--login` flag:
```bash
python fb_image_downloader.py "https://www.facebook.com/YOUR_ALBUM_LINK_HERE" --login
```
1. A Chrome browser will pop up. 
2. Log in to your Facebook account manually.
3. Return to your terminal and press **Enter**.

Your session will be saved to `fb_state.json`. For all future runs, you no longer need the `--login` flag; the script will automatically use your saved session and run in the background (headless) to scrape the images.

## Disclaimer

This tool is provided for educational purposes and personal use. Automated scraping of Facebook can violate their Terms of Service. The maintainers of this repository are not responsible for any bans, blocks, or legal issues you may face by using this tool. Use responsibly.
