# Facebook Media Extractor

A robust and reliable Python tool to scrape and download full resolution images from public Facebook links, specifically designed to handle dynamically loaded (lazy-loaded) Facebook albums.

## Features

- **Dynamic Scrolling:** Automatically scrolls to the bottom of large albums to capture every single post without missing any.
- **Multi-Media Extraction:** Scrapes images, videos (via `yt-dlp`), and text posts directly from the feed.
- **Login Support:** Securely bypasses Facebook's aggressive login walls by allowing you to authenticate locally and saving your session state.
- **Automated Downloads:** Filters out UI elements/emojis and seamlessly downloads the actual photos and videos to your local machine.

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

#### Windows
```cmd
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/facebook-media-extractor.git
cd facebook-media-extractor

# 2. Create a virtual environment and activate it
python -m venv venv
venv\Scripts\activate

# 3. Install the required Python packages
pip install -r requirements.txt
```

#### Linux
```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/facebook-media-extractor.git
cd facebook-media-extractor

# 2. Create a virtual environment and activate it
python3 -m venv venv
source venv/bin/activate

# 3. Install the required Python packages
pip install -r requirements.txt
```

#### macOS
```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/facebook-media-extractor.git
cd facebook-media-extractor

# 2. Create a virtual environment and activate it
python3 -m venv venv
source venv/bin/activate

# 3. Install the required Python packages
pip install -r requirements.txt
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

## Usage

### 🚀 Interactive Mode (Recommended)
The absolute easiest way to use this tool is the brand new interactive mode! Simply run the script with no arguments:
```bash
python fb_media_extractor.py
```
This will launch a friendly menu in your terminal:
```
=== Facebook Media Extractor ===
1. Download Images (Single URL or Album)
2. Download Videos (Single URL or Feed)
3. Download Posts (Text)
4. Download Full Profile (DP, Timeline, Photos, Videos)
5. Settings
6. Login (Generate Session Cookie)
7. Exit
```
Simply type the number of what you want to do and follow the prompts! 

**Cross-Platform Automatic Downloads**: 
By default, the script automatically figures out where your system's `Downloads` folder is (whether you're on Windows, macOS, Linux, or Android via Termux) and creates an `fb_media` folder inside it! You can change this default location inside the **Settings (Option 5)** menu.

---

### Command-Line Mode (For Power Users)

#### Basic Download (Single Pages/Albums)
If you prefer bypassing the menu, run:
```bash
python fb_media_extractor.py "https://www.facebook.com/YOUR_LINK_HERE" --type all
```
The `--type` flag controls what you download. Available options are `images` (default), `videos`, `posts`, or `all`.

#### Full Profile Extraction (Advanced)
If you want to download an *entire* user's profile, use the `--profile` flag and provide the base profile URL:
```bash
python fb_media_extractor.py "https://www.facebook.com/username" --type all --profile
```
Because full profiles can be massive, the script defaults to a maximum of 50 scrolls per tab to protect your account. You can increase this using the `--max-scrolls` flag or by changing it in the Interactive Settings menu:
```bash
python fb_media_extractor.py "https://www.facebook.com/username" --profile --max-scrolls 200
```
When using `--profile`, the media is automatically organized into a folder named after the username with subfolders for `dp_and_cover`, `images`, `videos`, and `posts`.

---

### Bypassing Login Blocks (For large albums or restricted content)
Facebook frequently blocks anonymous users from scrolling down. To bypass this, you need to provide your Facebook login cookies. The script looks for a file named `fb_cookies.json`. 

#### Method 1: Interactive Menu
Simply select **Option 6** from the interactive menu, log in through the popup browser, and press Enter.

#### Method 2: Command Line (Desktop/Termux:X11)
If you are on a desktop environment, or have a GUI set up in Termux (like Termux:X11), run the script once with the `--login` flag:
```bash
python fb_media_extractor.py --login
```
1. A Chrome browser will pop up. 
2. Log in to your Facebook account manually.
3. Return to your terminal and press **Enter**.

#### Method 3: The "No PC" Mobile Workaround for Termux
If you are using Termux on your phone and don't have a graphical interface set up, you can get the cookies directly from your phone's browser:
1. Download **Kiwi Browser** from the Google Play Store (it supports desktop Chrome extensions).
2. Install the [Cookie-Editor extension](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm).
3. Log into Facebook normally inside Kiwi Browser.
4. Tap the three dots menu, open the **Cookie-Editor** extension, and tap **Export** (this copies your cookies to your clipboard in perfect JSON format).
5. Go back to Termux and create the cookie file:
   ```bash
   nano fb_cookies.json
   ```
6. Paste the cookies from your clipboard, save the file (Ctrl+O, Enter), and exit (Ctrl+X).

## Disclaimer

This tool is provided for educational purposes and personal use. Automated scraping of Facebook can violate their Terms of Service. The maintainers of this repository are not responsible for any bans, blocks, or legal issues you may face by using this tool. Use responsibly.
