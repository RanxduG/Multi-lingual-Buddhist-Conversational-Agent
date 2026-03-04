#!/usr/bin/env python3
"""
Robust Selenium WebDriver implementation for Tripitaka scraping
Handles ChromeDriver issues with better error recovery and cleanup
"""

import os
import time
import subprocess
import signal
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class RobustWebDriver:
    def __init__(self):
        self.driver = None
        self.service = None
        
    def kill_existing_chrome_processes(self):
        """Kill any existing Chrome/ChromeDriver processes"""
        try:
            # Kill ChromeDriver processes
            subprocess.run(['pkill', '-f', 'chromedriver'], capture_output=True)
            # Kill Chrome processes (be more specific to avoid killing user's Chrome)
            subprocess.run(['pkill', '-f', 'Google Chrome.*--headless'], capture_output=True)
            time.sleep(2)  # Give processes time to terminate
        except Exception as e:
            print(f"⚠️  Warning: Could not kill existing processes: {e}")
    
    def setup_chrome_options(self):
        """Setup Chrome options for headless scraping"""
        chrome_options = Options()
        
        # Basic headless setup
        chrome_options.add_argument("--headless=new")  # Use new headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Window and rendering
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        
        # Performance optimizations
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript-harmony-shipping")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        
        # Stability improvements
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-popup-blocking")
        
        # Memory management
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--max_old_space_size=4096")
        
        return chrome_options
    
    def create_driver(self, max_retries=3):
        """Create WebDriver with retry logic"""
        for attempt in range(max_retries):
            try:
                print(f"🔄 Creating WebDriver (attempt {attempt + 1}/{max_retries})")
                
                # Clean up any existing processes
                if attempt > 0:
                    self.kill_existing_chrome_processes()
                
                # Setup Chrome options
                chrome_options = self.setup_chrome_options()
                
                # Create service
                self.service = Service(ChromeDriverManager().install())
                
                # Create driver
                self.driver = webdriver.Chrome(
                    service=self.service,
                    options=chrome_options
                )
                
                # Set timeouts
                self.driver.set_page_load_timeout(30)
                self.driver.implicitly_wait(10)
                
                print(f"✅ WebDriver created successfully")
                return self.driver
                
            except Exception as e:
                print(f"❌ WebDriver attempt {attempt + 1} failed: {str(e)[:100]}...")
                
                # Clean up failed attempt
                self.cleanup()
                
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to create WebDriver after {max_retries} attempts")
                
                # Wait before retry
                time.sleep(5)
    
    def scrape_page(self, url, wait_time=8):
        """Scrape a single page with the WebDriver"""
        try:
            print(f"📄 Loading: {url}")
            
            # Navigate to page
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(wait_time)
            
            # Get page source
            html_content = self.driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            title = "Untitled"
            title_selectors = ["h1", "h2", ".title", "title"]
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element and title_element.get_text(strip=True):
                    title = title_element.get_text(strip=True)
                    break
            
            # Extract Sinhala content
            sinhala_text = ""
            sinhala_selectors = [
                "[class*='sinhala']",
                ".sinhala",
                "[class*='sin']",
                "div:contains('ඒවං මේ සුතං')",
                "div:contains('මා විසින්')"
            ]
            
            for selector in sinhala_selectors:
                try:
                    elements = soup.select(selector)
                    if elements:
                        sinhala_text = " ".join([el.get_text(strip=True) for el in elements])
                        if len(sinhala_text) > 1000:  # Found substantial content
                            break
                except:
                    continue
            
            # Extract Pali content
            pali_text = ""
            pali_selectors = [
                "[class*='pali']",
                ".pali",
                "[class*='pal']"
            ]
            
            for selector in pali_selectors:
                try:
                    elements = soup.select(selector)
                    if elements:
                        pali_text = " ".join([el.get_text(strip=True) for el in elements])
                        if len(pali_text) > 500:  # Found substantial content
                            break
                except:
                    continue
            
            # Validate content
            is_valid = self.validate_content(sinhala_text, pali_text, title)
            
            print(f"📊 Title: {title}")
            print(f"📊 Sinhala: {len(sinhala_text)} chars")
            print(f"📊 Pali: {len(pali_text)} chars")
            print(f"📊 Valid: {is_valid}")
            
            return {
                "url": url,
                "title": title,
                "content": {
                    "sinhala": sinhala_text,
                    "pali": pali_text
                },
                "is_valid_content": is_valid,
                "content_quality": "valid" if is_valid else "invalid",
                "scraping_method": "selenium_robust"
            }
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return {
                "url": url,
                "title": "Error",
                "content": {"sinhala": "", "pali": ""},
                "is_valid_content": False,
                "content_quality": "error",
                "error": str(e)
            }
    
    def validate_content(self, sinhala_text, pali_text, title):
        """Validate if content is actual Buddhist text"""
        # Check for Buddhist indicators
        buddhist_indicators = [
            'ඒවං මේ සුතං',
            'මා විසින් මෙසේ අසන ලදී',
            'භාග්‍යවතුන් වහන්සේ',
            'භගවා',
            'භික්‍ෂූන් වහන්සේලා',
            'සාදු',
            'නිවන්'
        ]
        
        # Check for invalid indicators
        invalid_indicators = [
            'tripitaka.online',
            '© 1999',
            'Mahamevnawa',
            'Contact: info@'
        ]
        
        combined_text = (sinhala_text + " " + pali_text + " " + title).lower()
        
        # Check for invalid content first
        for indicator in invalid_indicators:
            if indicator.lower() in combined_text:
                return False
        
        # Must have substantial content
        if len(sinhala_text) < 500 and len(pali_text) < 200:
            return False
        
        # Check for Buddhist content indicators
        found_buddhist = 0
        for indicator in buddhist_indicators:
            if indicator in sinhala_text:
                found_buddhist += 1
        
        return found_buddhist > 0 or len(sinhala_text) > 5000
    
    def cleanup(self):
        """Clean up WebDriver resources"""
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass
        
        try:
            if self.service:
                self.service.stop()
        except:
            pass
        
        self.driver = None
        self.service = None
    
    def __enter__(self):
        """Context manager entry"""
        self.create_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()

def scrape_tripitaka_page_robust(url: str):
    """Main function to scrape a Tripitaka page with robust WebDriver"""
    with RobustWebDriver() as driver:
        return driver.scrape_page(url)

if __name__ == "__main__":
    # Test the robust scraper
    test_url = "https://tripitaka.online/sutta/265"
    print(f"🧪 Testing robust scraper with: {test_url}")
    result = scrape_tripitaka_page_robust(test_url)
    print(f"\n✅ Result: {result}")