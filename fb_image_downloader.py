import asyncio
import os
import requests
from playwright.async_api import async_playwright

async def download_images_from_fb(url, output_dir="fb_images", login_mode=False):
    """
    Scrapes images from a public Facebook link using Playwright.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    state_file = "fb_state.json"
    
    # Detect Termux (Android) environment
    is_termux = "com.termux" in os.environ.get("PREFIX", "")
    executable_path = None
    if is_termux:
        executable_path = "/data/data/com.termux/files/usr/bin/chromium"
        print("Detected Termux environment. Using system Chromium...")

    async with async_playwright() as p:
        # Launch browser in headed mode if user needs to log in, else headless
        launch_args = {"headless": not login_mode}
        if executable_path:
            launch_args["executable_path"] = executable_path
            # In Termux, running headed (login_mode) might require X11 setup (like Termux:X11). 
            # If they don't have it, login_mode will likely fail to open a window.
            
        browser = await p.chromium.launch(**launch_args)
        
        context_args = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        
        # Load existing cookies if available
        if os.path.exists(state_file):
            context_args["storage_state"] = state_file
            
        context = await browser.new_context(**context_args)
        page = await context.new_page()
        
        if login_mode:
            print("Opening Facebook for you to log in...")
            await page.goto("https://www.facebook.com")
            print("Please log in to your account in the browser window.")
            input("Press Enter here in the terminal AFTER you have successfully logged in...")
            # Save the state for future runs
            await context.storage_state(path=state_file)
            print(f"Session saved to {state_file}! You won't need to log in next time.")

        
        print(f"Navigating to {url}")
        try:
            await page.goto(url, timeout=60000)
        except Exception as e:
            print(f"Error navigating to page: {e}")
            await browser.close()
            return
        
        print("Scrolling to load dynamic content and collecting images...")
        image_urls = set()
        
        # Keep scrolling until we don't find any new images for a few consecutive scrolls
        max_scrolls = 50
        no_new_images_count = 0
        
        for i in range(max_scrolls):
            # Extract images currently in the DOM
            img_elements = await page.query_selector_all('img')
            current_count = len(image_urls)
            
            for img in img_elements:
                src = await img.get_attribute('src')
                if src and src.startswith('http') and 'emoji' not in src:
                    image_urls.add(src)
            
            new_count = len(image_urls)
            print(f"Scroll {i+1}: Found {new_count} total unique images so far...")
            
            if new_count == current_count:
                no_new_images_count += 1
            else:
                no_new_images_count = 0
                
            # If no new images were found for 3 consecutive scrolls, we likely reached the bottom
            if no_new_images_count >= 3:
                print("No new images found for 3 scrolls. Reached the bottom of the album.")
                break
                
            # Scroll to the very bottom of the page
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000) # Wait for network requests to load new images

        await browser.close()
        
        image_urls = list(image_urls)
        print(f"Found {len(image_urls)} potential images after full scroll.")
        
        downloaded_count = 0
        for i, img_url in enumerate(image_urls):
            try:
                response = requests.get(img_url, timeout=10)
                if response.status_code == 200:
                    # Filter out tiny images based on content length (e.g., < 5KB)
                    if len(response.content) > 5000:
                        filename = os.path.join(output_dir, f"image_{downloaded_count+1}.jpg")
                        with open(filename, 'wb') as f:
                            f.write(response.content)
                        print(f"Downloaded: {filename}")
                        downloaded_count += 1
            except Exception as e:
                print(f"Failed to download {img_url}: {e}")
                
        print(f"Successfully downloaded {downloaded_count} images to '{output_dir}/'.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python fb_image_downloader.py <facebook_public_link> [--login]")
        sys.exit(1)
        
    url = sys.argv[1]
    login_mode = len(sys.argv) > 2 and sys.argv[2] == "--login"
    
    # If the first argument is --login and no URL is provided, handle it
    if url == "--login":
        print("Please provide a URL: python fb_image_downloader.py <url> --login")
        sys.exit(1)
        
    asyncio.run(download_images_from_fb(url, login_mode=login_mode))
