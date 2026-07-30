import os
import time
import requests
import sys
import json
import argparse
import yt_dlp
import re
from urllib.parse import urlparse, urlunparse
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
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"Failed to download video {url}: {e}")
        return False

def scroll_and_collect(driver, media_types, max_scrolls=50):
    print("Scrolling to load dynamic content and collecting media...")
    image_urls = set()
    video_urls = set()
    post_texts = set()
    
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
                if len(text) > 20: 
                    post_texts.add(text)
        
        new_count = len(image_urls) + len(video_urls) + len(post_texts)
        print(f"Scroll {i+1}/{max_scrolls}: Found {len(image_urls)} images, {len(video_urls)} video links, {len(post_texts)} posts...")
        
        if new_count == current_count:
            no_new_content_count += 1
        else:
            no_new_content_count = 0
            
        if no_new_content_count >= 3:
            print("No new content found for 3 scrolls. Reached the bottom of the page.")
            break
            
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
    return list(image_urls), list(video_urls), list(post_texts)

def extract_media(url, media_types, base_output_dir="fb_media", login_mode=False, is_profile=False, max_scrolls=50):
    """
    Scrapes media from a public Facebook link using Selenium.
    """
    # Clean and parse URL for profile extraction
    parsed_url = urlparse(url)
    username = parsed_url.path.strip('/').split('/')[0]
    
    if is_profile:
        print(f"Profile mode enabled. Target username: {username}")
        base_output_dir = os.path.join(base_output_dir, username)

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
            return
    else:
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except ImportError:
            driver = webdriver.Chrome(options=chrome_options)

    try:
        print(f"Navigating to Facebook to load cookies...")
        driver.get("https://www.facebook.com")
        
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
        
        all_image_urls = set()
        all_video_urls = set()
        all_post_texts = set()

        if is_profile:
            base_profile_url = f"https://www.facebook.com/{username}"
            
            # 1. Main Timeline (for DP, Cover, and Posts)
            print(f"\n--- Scraping Profile Timeline: {base_profile_url} ---")
            driver.get(base_profile_url)
            time.sleep(3)
            i_urls, v_urls, p_texts = scroll_and_collect(driver, ["posts", "images"] if "all" in media_types else media_types, max_scrolls)
            all_image_urls.update(i_urls)
            all_video_urls.update(v_urls)
            all_post_texts.update(p_texts)
            
            # 2. Photos Tab
            if "images" in media_types or "all" in media_types:
                photos_url = f"{base_profile_url}/photos"
                print(f"\n--- Scraping Profile Photos: {photos_url} ---")
                driver.get(photos_url)
                time.sleep(3)
                i_urls, _, _ = scroll_and_collect(driver, ["images"], max_scrolls)
                all_image_urls.update(i_urls)
                
            # 3. Videos Tab
            if "videos" in media_types or "all" in media_types:
                videos_url = f"{base_profile_url}/videos"
                print(f"\n--- Scraping Profile Videos: {videos_url} ---")
                driver.get(videos_url)
                time.sleep(3)
                _, v_urls, _ = scroll_and_collect(driver, ["videos"], max_scrolls)
                all_video_urls.update(v_urls)
                
        else:
            # Single page scrape
            print(f"Navigating to URL: {url}")
            driver.get(url)
            time.sleep(3)
            i_urls, v_urls, p_texts = scroll_and_collect(driver, media_types, max_scrolls)
            all_image_urls.update(i_urls)
            all_video_urls.update(v_urls)
            all_post_texts.update(p_texts)

        print("\n--- Download Phase ---")
        
        if "images" in media_types or "all" in media_types:
            downloaded_count = 0
            for i, img_url in enumerate(list(all_image_urls)):
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
            downloaded_count = 0
            for v_url in list(all_video_urls):
                if download_video(v_url, videos_dir):
                    downloaded_count += 1
            print(f"Successfully downloaded {downloaded_count} videos to '{videos_dir}/'.")

        if "posts" in media_types or "all" in media_types:
            post_texts = list(all_post_texts)
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
    parser.add_argument("url", help="Public Facebook URL (or Profile URL if --profile is used)")
    parser.add_argument("--type", choices=['images', 'videos', 'posts', 'all'], default="images", help="Type of media to extract")
    parser.add_argument("--profile", action="store_true", help="Extract an entire user profile (navigates across Timeline, Photos, and Videos tabs)")
    parser.add_argument("--max-scrolls", type=int, default=50, help="Maximum number of scrolls per page (default: 50)")
    parser.add_argument("--login", action="store_true", help="Launch browser visibly to login and save session")
    
    args = parser.parse_args()
    
    extract_media(args.url, [args.type], login_mode=args.login, is_profile=args.profile, max_scrolls=args.max_scrolls)
