"""
Simple requests-based scraper for Tripitaka.online
Uses requests with session persistence instead of Selenium
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import os
from urllib.parse import urljoin

class SimpleRequestsScraper:
    """Simple scraper using requests instead of Selenium"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def scrape_page(self, url: str, delay: float = 1.0):
        """Scrape a single page using requests"""
        try:
            print(f"🌐 Scraping URL (requests): {url}")
            
            # Add delay to be respectful
            time.sleep(delay)
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = "Untitled"
            title_element = soup.find('title')
            if title_element:
                title = title_element.get_text(strip=True)
            
            # Try to extract any text content
            # This won't get JavaScript-rendered content, but will get static content
            text_content = soup.get_text(strip=True)
            
            # Look for specific content patterns
            sinhala_content = ""
            pali_content = ""
            
            # Try to find content in various ways
            # Look for divs with Sinhala/Pali content
            for div in soup.find_all('div'):
                div_text = div.get_text(strip=True)
                if len(div_text) > 100:  # Substantial content
                    if any(char in div_text for char in ['ඒ', 'අ', 'ම', 'භ']):  # Sinhala characters
                        if len(div_text) > len(sinhala_content):
                            sinhala_content = div_text
                    elif any(word in div_text.lower() for word in ['eva', 'buddha', 'bhante']):  # Pali words
                        if len(div_text) > len(pali_content):
                            pali_content = div_text
            
            # If no specific content found, use general text
            if not sinhala_content and len(text_content) > 200:
                sinhala_content = text_content[:2000]  # Limit to 2000 chars
            
            # Basic validation
            is_valid = len(sinhala_content) > 500 or len(pali_content) > 200
            if "tripitaka.online" in title.lower() and len(sinhala_content) < 2000:
                is_valid = False
            
            print(f"📄 Title: {title}")
            print(f"📊 Sinhala: {len(sinhala_content)} chars, Pali: {len(pali_content)} chars")
            print(f"✅ Valid: {is_valid}")
            
            return {
                "url": url,
                "title": title,
                "content": {
                    "sinhala": sinhala_content,
                    "pali": pali_content
                },
                "is_valid_content": is_valid,
                "content_quality": "requests_scrape",
                "scraping_method": "requests"
            }
            
        except requests.RequestException as e:
            print(f"❌ Request failed for {url}: {e}")
            return {
                "url": url,
                "title": "Error",
                "content": {"sinhala": "", "pali": ""},
                "error": str(e),
                "is_valid_content": False,
                "content_quality": "error",
                "scraping_method": "requests"
            }
        except Exception as e:
            print(f"❌ Unexpected error for {url}: {e}")
            return {
                "url": url,
                "title": "Error", 
                "content": {"sinhala": "", "pali": ""},
                "error": str(e),
                "is_valid_content": False,
                "content_quality": "error",
                "scraping_method": "requests"
            }

# Create a simple function that matches the original API
def scrape_tripitaka_page_simple(url: str):
    """Simple scraper function that can replace the Selenium version"""
    scraper = SimpleRequestsScraper()
    return scraper.scrape_page(url, delay=1.0)