#!/usr/bin/env python3
"""
WebDriver Pool for multi-threaded scraping
Pre-creates ChromeDriver instances to avoid simultaneous initialization conflicts
"""

import time
import threading
from queue import Queue
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class WebDriverPool:
    """Thread-safe pool of WebDriver instances"""
    
    def __init__(self, pool_size=3):
        """
        Initialize pool with pre-created WebDrivers
        
        Args:
            pool_size: Number of WebDriver instances to create
        """
        self.pool_size = pool_size
        self.drivers = Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        self._closed = False
        
        print(f"🔧 Initializing WebDriver pool with {pool_size} drivers...")
        self._create_pool()
        print(f"✅ WebDriver pool ready with {pool_size} drivers")
    
    def _setup_chrome_options(self):
        """Setup Chrome options for headless scraping"""
        chrome_options = Options()
        
        # Basic headless setup
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Window and rendering
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        
        # Performance optimizations
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        
        # Stability
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--disable-popup-blocking")
        
        # User agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
        
        return chrome_options
    
    def _create_single_driver(self, driver_id):
        """Create a single WebDriver instance"""
        try:
            print(f"  🔹 Creating driver {driver_id + 1}/{self.pool_size}...")
            
            chrome_options = self._setup_chrome_options()
            
            # Add a unique remote debugging port for each driver to avoid conflicts
            debug_port = 9222 + driver_id
            chrome_options.add_argument(f"--remote-debugging-port={debug_port}")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Set timeouts
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(5)
            
            # Small delay between driver creations to avoid conflicts
            time.sleep(2)
            
            return driver
            
        except Exception as e:
            print(f"  ❌ Failed to create driver {driver_id + 1}: {e}")
            raise
    
    def _create_pool(self):
        """Create all WebDriver instances sequentially"""
        for i in range(self.pool_size):
            try:
                driver = self._create_single_driver(i)
                self.drivers.put(driver)
            except Exception as e:
                print(f"❌ Failed to initialize driver pool: {e}")
                self.close_all()
                raise
    
    def acquire(self, timeout=60):
        """
        Get a WebDriver from the pool
        
        Args:
            timeout: Maximum time to wait for available driver
            
        Returns:
            WebDriver instance
        """
        if self._closed:
            raise RuntimeError("WebDriver pool is closed")
        
        driver = self.drivers.get(timeout=timeout)
        return driver
    
    def release(self, driver):
        """
        Return a WebDriver to the pool
        
        Args:
            driver: WebDriver instance to return
        """
        if not self._closed:
            self.drivers.put(driver)
    
    def scrape_page(self, url, wait_time=5):
        """
        Scrape a page using a driver from the pool
        
        Args:
            url: URL to scrape
            wait_time: Time to wait for page load (seconds)
            
        Returns:
            dict: Scraped data
        """
        driver = None
        try:
            driver = self.acquire()
            
            # Navigate to page
            driver.get(url)
            time.sleep(wait_time)
            
            # Get page source
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            title = "Untitled"
            title_element = soup.find('title')
            if title_element:
                title = title_element.get_text(strip=True)
            
            # Extract all text content
            body = soup.find('body')
            if body:
                # Remove script and style elements
                for script in body(["script", "style"]):
                    script.decompose()
                
                text_content = body.get_text(separator='\n', strip=True)
            else:
                text_content = soup.get_text(separator='\n', strip=True)
            
            # Try to separate Sinhala and Pali content
            # Look for specific divs/classes if they exist
            sinhala_content = ""
            pali_content = ""
            
            # Try common selectors
            sinhala_divs = soup.find_all(['div', 'p'], class_=lambda x: x and ('sinhala' in x.lower() or 'sin' in x.lower()))
            if sinhala_divs:
                sinhala_content = '\n'.join([div.get_text(strip=True) for div in sinhala_divs])
            
            pali_divs = soup.find_all(['div', 'p'], class_=lambda x: x and 'pali' in x.lower())
            if pali_divs:
                pali_content = '\n'.join([div.get_text(strip=True) for div in pali_divs])
            
            # If no specific divs found, try to extract from full text
            if not sinhala_content and not pali_content:
                # Use all text as sinhala for now
                sinhala_content = text_content
            
            # Validate content
            is_valid = self._validate_content(sinhala_content, pali_content, title)
            
            return {
                "url": url,
                "title": title,
                "content": {
                    "sinhala": sinhala_content,
                    "pali": pali_content
                },
                "is_valid_content": is_valid,
                "content_quality": "valid" if is_valid else "invalid",
                "scraping_method": "selenium_pool"
            }
            
        except Exception as e:
            return {
                "url": url,
                "title": "Error",
                "content": {"sinhala": "", "pali": ""},
                "is_valid_content": False,
                "content_quality": "error",
                "error": str(e),
                "scraping_method": "selenium_pool"
            }
        finally:
            if driver:
                self.release(driver)
    
    def _validate_content(self, sinhala_text, pali_text, title):
        """Validate if content is actual Buddhist text"""
        buddhist_indicators = [
            'ඒවං මේ සුතං',
            'මා විසින් මෙසේ අසන ලදී',
            'භාග්‍යවතුන් වහන්සේ',
            'භගවා',
            'භික්‍ෂූන් වහන්සේලා',
            'සාදු',
            'නිවන්'
        ]
        
        invalid_indicators = [
            'tripitaka.online',
            '© 1999',
            'Mahamevnawa',
            'Contact: info@'
        ]
        
        combined_text = (sinhala_text + " " + pali_text + " " + title).lower()
        
        # Check for invalid content
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
    
    def close_all(self):
        """Close all WebDriver instances in the pool"""
        with self.lock:
            self._closed = True
            
            print(f"🔒 Closing WebDriver pool...")
            while not self.drivers.empty():
                try:
                    driver = self.drivers.get_nowait()
                    driver.quit()
                except:
                    pass
            print(f"✅ WebDriver pool closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_all()


def scrape_with_pool(url: str, pool: WebDriverPool, wait_time=5):
    """
    Helper function to scrape using a WebDriver pool
    
    Args:
        url: URL to scrape
        pool: WebDriverPool instance
        wait_time: Wait time for page load
        
    Returns:
        dict: Scraped data
    """
    return pool.scrape_page(url, wait_time)
