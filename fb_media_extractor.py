import os
import time
import requests
import sys
import json
import argparse
import yt_dlp
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def download_video(url, output_dir):
    try:
        print(f"Attempting to download video from {url}...")
        ydl_opts = {
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            # Add cookiefile if you want yt-dlp to also use cookies (requires converting json to netscape format)
            # For public videos, it works without cookies usually.
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"Failed to download video {url}: {e}")
        return False

def extract_media(url, media_types, base_output_dir="fb_media", login_mode=False):
    """
    Scrapes media from a public Facebook link using Selenium.
    """
    images_dir = os.path.join(base_output_dir, "images")
    videos_dir = os.path.join(base_output_dir, "videos")
    posts_dir = os.path.join(base_output_dir, "posts")

    if "images" in media_types or "all" in media_types:
        os.makedirs(images_dir, exist_ok=True)
    if "videos" in media_types or "all" in media_types:
        os.makedirs(videos_dir, exist_ok=True)
    if "posts" in media_types or "all" in media_types:
        os.makedirs(posts_dir, exist_ok=True)

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
        chrome_options.binary_location = "/data/data/com.termux/files/usr/bin/chromium-browser"
        try:
            service = Service(executable_path="/data/data/com.termux/files/usr/bin/chromedriver")
            driver = webdriver.Chrome(service=service, options=chrome_options)
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
                    if 'sameSite' in cookie:
                        del cookie['sameSite']
                    driver.add_cookie(cookie)
            print("Cookies loaded!")

        if login_mode:
            print("Please log in to your account in the browser window.")
            input("Press Enter here in the terminal AFTER you have successfully logged in...")
            cookies = driver.get_cookies()
            with open(state_file, 'w') as f:
                json.dump(cookies, f)
            print(f"Session cookies saved to {state_file}! You won't need to log in next time.")
        
        print(f"Navigating to URL: {url}")
        driver.get(url)
        time.sleep(3) # Wait for initial load
        
        print("Scrolling to load dynamic content and collecting media...")
        image_urls = set()
        video_urls = set()
        post_texts = set()
        
        max_scrolls = 50
        no_new_content_count = 0
        
        for i in range(max_scrolls):
            current_count = len(image_urls) + len(video_urls) + len(post_texts)
            
            if "images" in media_types or "all" in media_types:
                img_elements = driver.find_elements(By.TAG_NAME, 'img')
                for img in img_elements:
                    src = img.get_attribute('src')
                    if src and src.startswith('http') and 'emoji' not in src:
                        image_urls.add(src)
                        
            if "videos" in media_types or "all" in media_types:
                a_elements = driver.find_elements(By.TAG_NAME, 'a')
                for a in a_elements:
                    href = a.get_attribute('href')
                    if href and ('/videos/' in href or '/watch' in href):
                        clean_href = href.split('?')[0] if '/videos/' in href else href
                        video_urls.add(clean_href)
                        
            if "posts" in media_types or "all" in media_types:
                text_elements = driver.find_elements(By.XPATH, '//div[@data-ad-comet-preview="message"] | //div[@dir="auto"]')
                for el in text_elements:
                    text = el.text.strip()
                    if len(text) > 20: # Ignore short meaningless text like "Like", "Share"
                        post_texts.add(text)
            
            new_count = len(image_urls) + len(video_urls) + len(post_texts)
            print(f"Scroll {i+1}: Found {len(image_urls)} images, {len(video_urls)} video links, {len(post_texts)} posts...")
            
            if new_count == current_count:
                no_new_content_count += 1
            else:
                no_new_content_count = 0
                
            if no_new_content_count >= 3:
                print("No new content found for 3 scrolls. Reached the bottom of the page.")
                break
                
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) # Wait for network requests

        print("\n--- Download Phase ---")
        
        if "images" in media_types or "all" in media_types:
            image_urls = list(image_urls)
            downloaded_count = 0
            for i, img_url in enumerate(image_urls):
                try:
                    response = requests.get(img_url, timeout=10)
                    if response.status_code == 200 and len(response.content) > 5000:
                        filename = os.path.join(images_dir, f"image_{downloaded_count+1}.jpg")
                        with open(filename, 'wb') as f:
                            f.write(response.content)
                        downloaded_count += 1
                except Exception as e:
                    pass
            print(f"Successfully downloaded {downloaded_count} images to '{images_dir}/'.")

        if "videos" in media_types or "all" in media_types:
            video_urls = list(video_urls)
            downloaded_count = 0
            for v_url in video_urls:
                if download_video(v_url, videos_dir):
                    downloaded_count += 1
            print(f"Successfully downloaded {downloaded_count} videos to '{videos_dir}/'.")

        if "posts" in media_types or "all" in media_types:
            post_texts = list(post_texts)
            for i, text in enumerate(post_texts):
                filename = os.path.join(posts_dir, f"post_{i+1}.txt")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(text)
            print(f"Successfully saved {len(post_texts)} post texts to '{posts_dir}/'.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract Media from Facebook")
    parser.add_argument("url", help="Public Facebook URL")
    parser.add_argument("--type", choices=['images', 'videos', 'posts', 'all'], default="images", help="Type of media to extract")
    parser.add_argument("--login", action="store_true", help="Launch browser visibly to login and save session")
    
    args = parser.parse_args()
    
    extract_media(args.url, [args.type], login_mode=args.login)
