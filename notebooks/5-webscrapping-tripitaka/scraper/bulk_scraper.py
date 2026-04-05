import json
import os
import time
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.nikaya_config import NIKAYA_RANGES, get_nikaya_info, print_nikaya_summary
try:
    from .webdriver_pool import WebDriverPool
    selenium_available = True
except ImportError:
    selenium_available = False
    print("⚠️  Selenium not available, will use fallback scraper")

from .simple_requests_scraper import scrape_tripitaka_page_simple

class BulkTripitakaScraper:
    def __init__(self, output_dir="output/bulk", max_workers=3, delay_between_requests=1.0, skip_invalid=False, use_selenium=True):
        """
        Initialize the bulk scraper
        
        Args:
            output_dir: Directory to save scraped data
            max_workers: Number of parallel workers (keep low to be respectful)
            delay_between_requests: Delay in seconds between requests
            skip_invalid: Whether to skip invalid content (False = capture all content)
            use_selenium: Whether to use Selenium (True) or simple requests (False)
        """
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.delay_between_requests = delay_between_requests
        self.skip_invalid = skip_invalid
        self.use_selenium = use_selenium and selenium_available
        self.scraped_count = 0
        self.error_count = 0
        self.lock = threading.Lock()
        self.webdriver_pool = None
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Progress tracking
        self.start_time = None
        self.progress_file = os.path.join(output_dir, "scraping_progress.json")
        self.error_log_file = os.path.join(output_dir, "error_log.json")
        
    def find_valid_sutta_range(self, start=1, max_check=100000, sample_size=100):
        """
        Use predefined Nikaya ranges instead of sampling
        
        Returns:
            tuple: (min_sutta, max_sutta, total_estimated)
        """
        print(f"� Using predefined Nikaya structure...")
        print_nikaya_summary()
        
        # Calculate total from all Nikayas
        total_suttas = 0
        min_sutta = float('inf')
        max_sutta = 0
        
        for nikaya_info in NIKAYA_RANGES.values():
            range_size = nikaya_info["end"] - nikaya_info["start"] + 1
            total_suttas += range_size
            min_sutta = min(min_sutta, nikaya_info["start"])
            max_sutta = max(max_sutta, nikaya_info["end"])
        
        return min_sutta, max_sutta, total_suttas
    
    def get_sutta_urls(self, start=1, end=None, step=1):
        """
        Generate sutta URLs in the given range
        
        Args:
            start: Starting sutta number
            end: Ending sutta number (if None, will auto-detect)
            step: Step size
            
        Returns:
            list: List of sutta URLs
        """
        if end is None:
            print("🔍 Auto-detecting sutta range...")
            _, max_sutta, estimated_total = self.find_valid_sutta_range()
            end = min(max_sutta + 1000, 100000)  # Add buffer but cap at 100k
            print(f"📊 Will scrape suttas from {start} to {end}")
        
        urls = []
        for i in range(start, end + 1, step):
            urls.append(f"https://tripitaka.online/sutta/{i}")
        
        return urls
    
    def scrape_single_sutta(self, url):
        """
        Scrape a single sutta with error handling
        
        Args:
            url: URL to scrape
            
        Returns:
            dict: Scraped data or None if error
        """
        try:
            # Extract sutta number from URL
            sutta_num = url.split('/')[-1]
            
            # Add delay to be respectful
            time.sleep(self.delay_between_requests)
            
            # Scrape the content
            if self.use_selenium and self.webdriver_pool:
                # Use Selenium WebDriver pool for JavaScript-rendered content
                data = self.webdriver_pool.scrape_page(url, wait_time=5)
            else:
                # Use simple requests scraper for static content
                data = scrape_tripitaka_page_simple(url)
            
            # Validate that we got content
            if not data or not data.get('content'):
                raise ValueError("No content scraped")
            
            sinhala_content = data['content'].get('sinhala', '')
            pali_content = data['content'].get('pali', '')
            
            if not sinhala_content and not pali_content:
                raise ValueError("No Sinhala or Pali content found")
                
            # Check if content is valid (not just navigation/footer)
            is_valid = data.get('is_valid_content', False)
            # For raw extraction mode, we'll keep all content and let data cleaning handle filtering
            if self.skip_invalid and not is_valid:
                print(f"⚠️  Skipping sutta {sutta_num}: Invalid/empty content detected")
                return None  # Skip invalid content based on flag
            
            # Add metadata
            data['sutta_number'] = int(sutta_num)
            data['scraped_at'] = datetime.now().isoformat()
            data['word_counts'] = {
                'sinhala': len(sinhala_content.split()) if sinhala_content else 0,
                'pali': len(pali_content.split()) if pali_content else 0
            }
            
            # Add Nikaya information
            nikaya_info = get_nikaya_info(int(sutta_num))
            data['nikaya'] = nikaya_info
            
            with self.lock:
                self.scraped_count += 1
                if self.scraped_count % 10 == 0:
                    self.save_progress()
                    elapsed = time.time() - self.start_time.timestamp() if self.start_time else 0
                    rate = self.scraped_count / elapsed * 60 if elapsed > 0 else 0
                    nikaya_name = nikaya_info['name'] if nikaya_info else 'Unknown'
                    print(f"✅ Scraped {self.scraped_count} suttas (Rate: {rate:.1f}/min, Current: {nikaya_name})")
            
            return data
            
        except Exception as e:
            error_info = {
                'url': url,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
            with self.lock:
                self.error_count += 1
                print(f"❌ Error scraping {url}: {e}")
                
                # Log error
                self.log_error(error_info)
            
            return None
    
    def log_error(self, error_info):
        """Log error to error log file"""
        try:
            if os.path.exists(self.error_log_file):
                with open(self.error_log_file, 'r', encoding='utf-8') as f:
                    errors = json.load(f)
            else:
                errors = []
            
            errors.append(error_info)
            
            with open(self.error_log_file, 'w', encoding='utf-8') as f:
                json.dump(errors, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to log error: {e}")
    
    def save_progress(self):
        """Save current progress"""
        progress = {
            'scraped_count': self.scraped_count,
            'error_count': self.error_count,
            'last_update': datetime.now().isoformat(),
            'start_time': self.start_time.isoformat() if self.start_time else None
        }
        
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save progress: {e}")
    
    def scrape_bulk(self, start=1, end=None, batch_size=100):
        """
        Scrape suttas in bulk
        
        Args:
            start: Starting sutta number
            end: Ending sutta number
            batch_size: Number of suttas to scrape per batch file
        """
        self.start_time = datetime.now()
        print(f"🚀 Starting bulk scraping at {self.start_time}")
        
        # Initialize WebDriver pool if using Selenium
        if self.use_selenium:
            print(f"🌐 Using Selenium with WebDriver pool ({self.max_workers} drivers)")
            self.webdriver_pool = WebDriverPool(pool_size=self.max_workers)
        else:
            print(f"🌐 Using simple requests scraper (no Selenium)")
        
        # Get URLs to scrape
        urls = self.get_sutta_urls(start, end)
        total_urls = len(urls)
        print(f"📊 Total URLs to scrape: {total_urls}")
        
        # Create batches
        batches = [urls[i:i + batch_size] for i in range(0, len(urls), batch_size)]
        print(f"📊 Created {len(batches)} batches of {batch_size} suttas each")
        
        # Process each batch
        for batch_idx, batch_urls in enumerate(batches):
            print(f"\n📦 Processing batch {batch_idx + 1}/{len(batches)}")
            batch_data = []
            
            # Use ThreadPoolExecutor for concurrent scraping (but limited workers)
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_url = {executor.submit(self.scrape_single_sutta, url): url 
                               for url in batch_urls}
                
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        data = future.result()
                        if data:
                            batch_data.append(data)
                    except Exception as e:
                        print(f"❌ Exception in thread for {url}: {e}")
            
            # Save batch
            if batch_data:
                batch_filename = os.path.join(self.output_dir, f"suttas_batch_{batch_idx + 1:04d}.json")
                self.save_batch(batch_data, batch_filename)
                print(f"💾 Saved batch {batch_idx + 1} with {len(batch_data)} suttas to {batch_filename}")
        
        # Clean up WebDriver pool
        if self.webdriver_pool:
            self.webdriver_pool.close_all()
            self.webdriver_pool = None
        
        # Final summary
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print(f"\n🎉 Bulk scraping completed!")
        print(f"📊 Total scraped: {self.scraped_count}")
        print(f"❌ Total errors: {self.error_count}")
        print(f"⏱️  Duration: {duration}")
        print(f"📈 Average rate: {self.scraped_count / duration.total_seconds() * 60:.2f} suttas/minute")
        
        self.save_progress()
    
    def scrape_nikaya(self, nikaya_key: str, batch_size=100):
        """
        Scrape a specific Nikaya collection
        
        Args:
            nikaya_key: Key from NIKAYA_RANGES (e.g., 'digha', 'majjhima', etc.)
            batch_size: Number of suttas to scrape per batch file
        """
        if nikaya_key not in NIKAYA_RANGES:
            available_keys = list(NIKAYA_RANGES.keys())
            raise ValueError(f"Invalid nikaya_key '{nikaya_key}'. Available: {available_keys}")
        
        nikaya_info = NIKAYA_RANGES[nikaya_key]
        print(f"🔸 Starting {nikaya_info['name']} ({nikaya_info['name_en']}) scraping")
        print(f"📊 Range: {nikaya_info['start']} - {nikaya_info['end']}")
        
        # Use specific output directory for this Nikaya
        nikaya_output_dir = os.path.join(self.output_dir, nikaya_key)
        os.makedirs(nikaya_output_dir, exist_ok=True)
        
        # Update output directory for this scraping session
        original_output_dir = self.output_dir
        self.output_dir = nikaya_output_dir
        
        try:
            # Scrape this Nikaya range
            self.scrape_bulk(
                start=nikaya_info['start'],
                end=nikaya_info['end'],
                batch_size=batch_size
            )
        finally:
            # Restore original output directory
            self.output_dir = original_output_dir
    
    def scrape_all_nikayas(self, batch_size=100, nikaya_order=None):
        """
        Scrape all Nikayas in sequence
        
        Args:
            batch_size: Number of suttas per batch file
            nikaya_order: List of nikaya keys in desired order, or None for default
        """
        if nikaya_order is None:
            # Default order: smallest to largest (traditional order)
            nikaya_order = ['digha', 'majjhima', 'samyutta', 'khuddaka', 'anguttara']
        
        print(f"🚀 Starting complete Tripitaka scraping in order: {nikaya_order}")
        print_nikaya_summary()
        
        overall_start_time = datetime.now()
        overall_scraped = 0
        overall_errors = 0
        
        for nikaya_key in nikaya_order:
            print(f"\n" + "="*60)
            print(f"📚 Starting {NIKAYA_RANGES[nikaya_key]['name']}")
            print("="*60)
            
            # Reset counters for this Nikaya
            self.scraped_count = 0
            self.error_count = 0
            
            try:
                self.scrape_nikaya(nikaya_key, batch_size)
                overall_scraped += self.scraped_count
                overall_errors += self.error_count
            except Exception as e:
                print(f"❌ Error scraping {nikaya_key}: {e}")
                continue
        
        # Final summary
        end_time = datetime.now()
        duration = end_time - overall_start_time
        
        print(f"\n" + "="*60)
        print(f"🎉 COMPLETE TRIPITAKA SCRAPING FINISHED!")
        print("="*60)
        print(f"📊 Total scraped: {overall_scraped:,}")
        print(f"❌ Total errors: {overall_errors:,}")
        print(f"⏱️  Total duration: {duration}")
        print(f"📈 Average rate: {overall_scraped / duration.total_seconds() * 60:.1f} suttas/minute")
        print("="*60)
    
    def save_batch(self, batch_data, filename):
        """Save a batch of scraped data"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(batch_data, f, ensure_ascii=False, indent=2)
    
    def resume_from_progress(self):
        """Resume scraping from saved progress"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)
                self.scraped_count = progress.get('scraped_count', 0)
                self.error_count = progress.get('error_count', 0)
                print(f"📋 Resuming from progress: {self.scraped_count} scraped, {self.error_count} errors")
                return True
        return False