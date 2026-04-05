import argparse
import sys
from scraper.tripitaka_scraper import scrape_tripitaka_page, save_json
from scraper.bulk_scraper import BulkTripitakaScraper
from config.nikaya_config import NIKAYA_RANGES, print_nikaya_summary

def scrape_single(url, output_file):
    """Scrape a single sutta"""
    print(f"🔍 Scraping single URL: {url}")
    data = scrape_tripitaka_page(url)
    save_json(data, output_file)
    print(f"✅ Scraped and saved {output_file}")

def scrape_bulk(start, end, batch_size, max_workers, delay, use_selenium=True):
    """Scrape multiple suttas in bulk"""
    print(f"🚀 Starting bulk scraping from sutta {start} to {end if end else 'auto-detect'}")
    
    scraper = BulkTripitakaScraper(
        output_dir="output/bulk",
        max_workers=max_workers,
        delay_between_requests=delay,
        use_selenium=use_selenium
    )
    
    # Try to resume from previous progress
    scraper.resume_from_progress()
    
    # Start bulk scraping
    scraper.scrape_bulk(start=start, end=end, batch_size=batch_size)

def scrape_nikaya(nikaya_key, batch_size, max_workers, delay, raw_mode=True, use_selenium=True):
    """Scrape a specific Nikaya"""
    if nikaya_key not in NIKAYA_RANGES:
        print(f"❌ Invalid Nikaya key: {nikaya_key}")
        print(f"Available options: {list(NIKAYA_RANGES.keys())}")
        sys.exit(1)
    
    nikaya_info = NIKAYA_RANGES[nikaya_key]
    print(f"🔸 Starting {nikaya_info['name']} ({nikaya_info['name_en']}) scraping")
    print(f"📊 Range: {nikaya_info['start']} - {nikaya_info['end']} ({nikaya_info['end'] - nikaya_info['start'] + 1:,} suttas)")
    
    if raw_mode:
        print("🔧 RAW MODE: Capturing ALL content (no filtering) - will clean data later")
    
    scraper = BulkTripitakaScraper(
        output_dir=f"output/raw_nikayas/{nikaya_key}",
        max_workers=max_workers,
        delay_between_requests=delay,
        skip_invalid=not raw_mode,  # If raw_mode=True, skip_invalid=False
        use_selenium=use_selenium
    )
    
    # Use the exact Nikaya ranges
    scraper.scrape_bulk(
        start=nikaya_info['start'],
        end=nikaya_info['end'],
        batch_size=batch_size
    )

def scrape_all_nikayas(batch_size, max_workers, delay):
    """Scrape all Nikayas"""
    print(f"🚀 Starting complete Tripitaka scraping")
    
    scraper = BulkTripitakaScraper(
        output_dir="output/complete_tripitaka",
        max_workers=max_workers,
        delay_between_requests=delay,
        use_selenium=True  # Use Selenium for JavaScript content
    )
    
    scraper.scrape_all_nikayas(batch_size)

def main():
    parser = argparse.ArgumentParser(description="Tripitaka.online scraper")
    parser.add_argument("--mode", choices=["single", "bulk", "nikaya", "all", "info", "test"], 
                       default="single", help="Scraping mode")
    
    # Single mode arguments
    parser.add_argument("--url", default="https://tripitaka.online/sutta/17",
                       help="URL to scrape (for single mode)")
    parser.add_argument("--output", default="output/samples/sutta.json",
                       help="Output file (for single mode)")
    
    # Bulk mode arguments
    parser.add_argument("--start", type=int, default=1,
                       help="Starting sutta number (for bulk mode)")
    parser.add_argument("--end", type=int, default=None,
                       help="Ending sutta number (for bulk mode, auto-detect if not specified)")
    
    # Nikaya mode arguments
    parser.add_argument("--nikaya", choices=list(NIKAYA_RANGES.keys()),
                       help="Specific Nikaya to scrape")
    
    # Common arguments
    parser.add_argument("--batch-size", type=int, default=100,
                       help="Number of suttas per batch file")
    parser.add_argument("--max-workers", type=int, default=2,
                       help="Maximum number of parallel workers")
    parser.add_argument("--delay", type=float, default=1.0,
                       help="Delay between requests in seconds")
    parser.add_argument("--raw", action="store_true",
                       help="Raw mode: capture all content without filtering (recommended)")
    parser.add_argument("--no-selenium", action="store_true",
                       help="Use simple requests instead of Selenium (faster but may miss JS content)")
    
    args = parser.parse_args()
    
    try:
        if args.mode == "info":
            print_nikaya_summary()
            
        elif args.mode == "single":
            scrape_single(args.url, args.output)
            
        elif args.mode == "test":
            print("🧪 Running test scrape on a small batch from each Nikaya...")
            scraper = BulkTripitakaScraper(
                output_dir="output/test_nikayas",
                max_workers=1,
                delay_between_requests=2.0,
                use_selenium=True  # Use Selenium for JavaScript content
            )
            
            # Test a few suttas from each Nikaya
            test_ranges = {
                "digha": (17, 19),      # Test 3 Digha suttas
                "majjhima": (265, 267), # Test 3 Majjhima suttas  
                "samyutta": (980, 982), # Test 3 Samyutta suttas
            }
            
            for nikaya_key, (start, end) in test_ranges.items():
                print(f"\n🧪 Testing {NIKAYA_RANGES[nikaya_key]['name']}...")
                scraper.scrape_bulk(start=start, end=end, batch_size=5)
            
        elif args.mode == "nikaya":
            if not args.nikaya:
                print("❌ --nikaya argument required for nikaya mode")
                print(f"Available options: {list(NIKAYA_RANGES.keys())}")
                sys.exit(1)
            scrape_nikaya(args.nikaya, args.batch_size, args.max_workers, args.delay, args.raw, not args.no_selenium)
            
        elif args.mode == "all":
            scrape_all_nikayas(args.batch_size, args.max_workers, args.delay)
            
        elif args.mode == "bulk":
            scrape_bulk(args.start, args.end, args.batch_size, args.max_workers, args.delay, not args.no_selenium)
            
        else:
            print("❌ Invalid mode specified")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Scraping interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # If no arguments provided, show help and run single mode as default
    if len(sys.argv) == 1:
        print("🔍 No arguments provided. Showing Tripitaka structure and running single sutta scrape.")
        print("Use --help to see all options.\n")
        print_nikaya_summary()
        print("\n" + "="*60)
        scrape_single("https://tripitaka.online/sutta/17", "output/samples/sutta_17.json")
    else:
        main()
