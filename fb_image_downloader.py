import os
import time
import requests
import sys
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def download_images_from_fb(url, output_dir="fb_images", login_mode=False):
    """
    Scrapes images from a public Facebook link using Selenium.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    state_file = "fb_cookies.json"
    
    # Detect Termux (Android) environment
    is_termux = "com.termux" in os.environ.get("PREFIX", "")
    
    chrome_options = Options()
    if not login_mode:
        chrome_options.add_argument("--headless=new")
        
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

    driver = None
    if is_termux:
        print("Detected Termux environment. Using system Chromium...")
        chrome_options.binary_location = "/data/data/com.termux/files/usr/bin/chromium"
        # In Termux, chromedriver should be installed via pkg and available in PATH
        # Usually it's in /data/data/com.termux/files/usr/bin/chromedriver
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print("Failed to start Chromium on Termux. Make sure 'chromedriver' package is installed.")
            print(f"Error details: {e}")
            return
    else:
        # Standard desktop: use webdriver_manager
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except ImportError:
            print("webdriver-manager is not installed. Attempting to use system chromedriver...")
            driver = webdriver.Chrome(options=chrome_options)

    try:
        print(f"Navigating to Facebook...")
        driver.get("https://www.facebook.com")
        
        # Load cookies if they exist and we are not forcing login
        if os.path.exists(state_file) and not login_mode:
            with open(state_file, 'r') as f:
                cookies = json.load(f)
                for cookie in cookies:
                    # Selenium requires strictly proper cookie dicts
                    if 'sameSite' in cookie:
                        del cookie['sameSite']
                    driver.add_cookie(cookie)
            print("Cookies loaded!")

        if login_mode:
            print("Please log in to your account in the browser window.")
            input("Press Enter here in the terminal AFTER you have successfully logged in...")
            # Save cookies
            cookies = driver.get_cookies()
            with open(state_file, 'w') as f:
                json.dump(cookies, f)
            print(f"Session cookies saved to {state_file}! You won't need to log in next time.")
        
        print(f"Navigating to album: {url}")
        driver.get(url)
        time.sleep(3) # Wait for initial load
        
        print("Scrolling to load dynamic content and collecting images...")
        image_urls = set()
        
        max_scrolls = 50
        no_new_images_count = 0
        
        for i in range(max_scrolls):
            img_elements = driver.find_elements(By.TAG_NAME, 'img')
            current_count = len(image_urls)
            
            for img in img_elements:
                src = img.get_attribute('src')
                if src and src.startswith('http') and 'emoji' not in src:
                    image_urls.add(src)
            
            new_count = len(image_urls)
            print(f"Scroll {i+1}: Found {new_count} total unique images so far...")
            
            if new_count == current_count:
                no_new_images_count += 1
            else:
                no_new_images_count = 0
                
            if no_new_images_count >= 3:
                print("No new images found for 3 scrolls. Reached the bottom of the album.")
                break
                
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) # Wait for network requests

        image_urls = list(image_urls)
        print(f"Found {len(image_urls)} potential images after full scroll.")
        
        downloaded_count = 0
        for i, img_url in enumerate(image_urls):
            try:
                response = requests.get(img_url, timeout=10)
                if response.status_code == 200:
                    if len(response.content) > 5000:
                        filename = os.path.join(output_dir, f"image_{downloaded_count+1}.jpg")
                        with open(filename, 'wb') as f:
                            f.write(response.content)
                        print(f"Downloaded: {filename}")
                        downloaded_count += 1
            except Exception as e:
                print(f"Failed to download {img_url}: {e}")
                
        print(f"Successfully downloaded {downloaded_count} images to '{output_dir}/'.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python fb_image_downloader.py <facebook_public_link> [--login]")
        sys.exit(1)
        
    url = sys.argv[1]
    login_mode = len(sys.argv) > 2 and sys.argv[2] == "--login"
    
    if url == "--login":
        print("Please provide a URL: python fb_image_downloader.py <url> --login")
        sys.exit(1)
        
    download_images_from_fb(url, login_mode=login_mode)
