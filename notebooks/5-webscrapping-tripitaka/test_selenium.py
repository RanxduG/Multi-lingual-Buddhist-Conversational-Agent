#!/usr/bin/env python3
"""
Test Selenium ChromeDriver setup
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def test_chromedriver():
    """Test if ChromeDriver can be initialized"""
    try:
        print('📥 Downloading/locating ChromeDriver...')
        
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        service = Service(ChromeDriverManager().install())
        print(f'✅ ChromeDriver path: {service.path}')
        
        print('🚀 Starting ChromeDriver...')
        driver = webdriver.Chrome(service=service, options=options)
        
        print('🌐 Testing with a simple page...')
        driver.get('https://www.google.com')
        
        print(f'✅ Page title: {driver.title}')
        print('✅ ChromeDriver is working correctly!')
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f'❌ ChromeDriver test failed: {e}')
        print(f'\nTroubleshooting steps:')
        print('1. Clear cache: rm -rf ~/.wdm')
        print('2. Update Chrome: Make sure Chrome browser is up to date')
        print('3. Reinstall webdriver-manager: pip install --upgrade webdriver-manager')
        return False

if __name__ == '__main__':
    test_chromedriver()
