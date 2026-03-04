"""
Persistent WebDriver Manager for Tripitaka Scraping
Maintains a single WebDriver instance to avoid connection issues
"""

import time
import atexit
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class PersistentWebDriver:
    """Singleton WebDriver manager that maintains one driver instance"""
    
    _instance = None
    _driver = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self._setup_driver()
            # Register cleanup at exit
            atexit.register(self.cleanup)
    
    def _setup_driver(self):
        """Initialize the Chrome WebDriver with optimal settings"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        
        try:
            service = Service(ChromeDriverManager().install())
            self._driver = webdriver.Chrome(service=service, options=chrome_options)
            self._driver.set_page_load_timeout(30)
            print("✅ Persistent WebDriver initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize persistent WebDriver: {e}")
            self._driver = None
    
    def get_driver(self):
        """Get the WebDriver instance, reinitialize if needed"""
        if self._driver is None:
            print("🔄 WebDriver not available, attempting to reinitialize...")
            self._setup_driver()
        
        return self._driver
    
    def cleanup(self):
        """Clean up the WebDriver"""
        if self._driver:
            try:
                self._driver.quit()
                print("🧹 WebDriver cleaned up successfully")
            except Exception as e:
                print(f"⚠️  Error during WebDriver cleanup: {e}")
            finally:
                self._driver = None
    
    def restart_if_needed(self):
        """Restart WebDriver if it becomes unresponsive"""
        try:
            # Test if driver is responsive
            if self._driver:
                self._driver.current_url
        except Exception:
            print("🔄 WebDriver became unresponsive, restarting...")
            self.cleanup()
            self._setup_driver()

# Global instance
webdriver_manager = PersistentWebDriver()

def get_persistent_driver():
    """Get the persistent WebDriver instance"""
    return webdriver_manager.get_driver()

def restart_persistent_driver():
    """Restart the persistent WebDriver if needed"""
    webdriver_manager.restart_if_needed()