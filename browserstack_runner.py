"""
BrowserStack Runner for El País Web Scraping Project
Executes the scraping solution across 5 parallel threads on BrowserStack
"""
import sys
import os
import time
import threading
from queue import Queue

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import ElPaisScraper
from translator import Translator
from text_analyzer import TextAnalyzer
from config import (
    BROWSERSTACK_USERNAME,
    BROWSERSTACK_ACCESS_KEY,
    BROWSERSTACK_BROWSERS,
    MAX_ARTICLES,
    IMAGE_DOWNLOAD_PATH
)


class BrowserStackRunner:
    """Runner for executing tests on BrowserStack with parallel threads"""
    
    def __init__(self):
        self.results = []
        self.lock = threading.Lock()
        self.num_threads = 5
        
    def create_browserstack_driver(self, browser_config):
        """
        Create a BrowserStack WebDriver
        
        Args:
            browser_config: Browser configuration dictionary
            
        Returns:
            WebDriver instance
        """
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.remote.webdriver import WebDriver
        
        # Build the BrowserStack URL
        bs_url = f"https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}@hub.browserstack.com/wd/hub"
        
        # Build capabilities
        capabilities = {
            "browserName": browser_config.get("browser", "Chrome"),
            "browserVersion": browser_config.get("browser_version", "latest"),
            "os": browser_config.get("os", "Windows"),
            "osVersion": browser_config.get("os_version", "10"),
            "resolution": "1920x1080",
            "browserstack.username": BROWSERSTACK_USERNAME,
            "browserstack.accessKey": BROWSERSTACK_ACCESS_KEY,
            "browserstack.networkLogs": "true",
            "browserstack.consoleLogs": "info",
            "acceptInsecureCerts": True
        }
        
        # Add device for mobile testing
        if "device" in browser_config:
            capabilities["device"] = browser_config["device"]
            capabilities["browserName"] = browser_config.get("browser", "Chrome")
        
        # Create Chrome options with Spanish language
        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", {"intl.accept_languages": "es"})
        
        try:
            driver = WebDriver(command_executor=bs_url, options=chrome_options)
            driver.implicitly_wait(10)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            print(f"Error creating BrowserStack driver for {browser_config.get('name', 'Unknown')}: {e}")
            return None
    
    def run_on_browser(self, browser_config, thread_id):
        """
        Run scraping on a specific browser configuration
        
        Args:
            browser_config: Browser configuration dictionary
            thread_id: Thread identifier
            
        Returns:
            dict: Result of the execution
        """
        browser_name = browser_config.get("name", "Unknown")
        
        print(f"\n{'='*60}")
        print(f"THREAD {thread_id}: Starting on {browser_name}")
        print(f"{'='*60}")
        
        result = {
            "thread_id": thread_id,
            "browser": browser_name,
            "success": False,
            "articles_scraped": 0,
            "error": None
        }
        
        driver = None
        
        try:
            # Create BrowserStack driver
            driver = self.create_browserstack_driver(browser_config)
            
            if not driver:
                result["error"] = "Failed to create driver"
                return result
            
            # Create scraper
            scraper = ElPaisScraper(driver=driver, is_browserstack=True)
            
            # Scrape articles
            articles = scraper.scrape_all_articles()
            
            result["articles_scraped"] = len(articles)
            
            if articles:
                # Translate titles
                spanish_titles = [article["title"] for article in articles if article["title"]]
                translator = Translator()
                english_titles = translator.translate_titles(spanish_titles)
                
                # Analyze headers
                analyzer = TextAnalyzer(min_repeat_count=2)
                repeated = analyzer.find_repeated_words(english_titles)
                
                result["repeated_words"] = repeated
                result["success"] = True
                
                print(f"\nTHREAD {thread_id}: Scraped {len(articles)} articles")
                print(f"THREAD {thread_id}: Found {len(repeated)} repeated words")
                
                # Set BrowserStack session status to passed
                driver.execute_script(
                    'browserstack_executor: {"action": "setSessionStatus", '
                    '"arguments": {"status":"passed","reason": "All steps executed successfully"}}'
                )
            
            # Close driver
            if driver:
                driver.quit()
                
        except Exception as e:
            result["error"] = str(e)
            print(f"THREAD {thread_id}: Error - {e}")
            
            # Set BrowserStack session status to failed
            if driver:
                try:
                    driver.execute_script(
                        'browserstack_executor: {"action": "setSessionStatus", '
                        '"arguments": {"status":"failed","reason": "' + str(e) + '"}}'
                    )
                except:
                    pass
            
        finally:
            # Make sure to quit the driver
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        
        # Store result
        with self.lock:
            self.results.append(result)
        
        print(f"\nTHREAD {thread_id}: Completed on {browser_name}")
        
        return result
    
    def run_parallel(self):
        """
        Run scraping on multiple browsers in parallel
        
        Returns:
            list: List of results from each browser
        """
        print("="*80)
        print("BROWSERSTACK PARALLEL EXECUTION")
        print("="*80)
        print(f"\nRunning on {len(BROWSERSTACK_BROWSERS)} browsers:")
        
        for i, browser in enumerate(BROWSERSTACK_BROWSERS):
            print(f"  {i+1}. {browser.get('name', 'Unknown')}")
        
        print(f"\nStarting {self.num_threads} parallel threads...")
        
        # Use ThreadPoolExecutor for parallel execution
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        threads = []
        
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            # Submit all tasks
            futures = {}
            
            for i, browser_config in enumerate(BROWSERSTACK_BROWSERS):
                future = executor.submit(self.run_on_browser, browser_config, i+1)
                futures[future] = browser_config.get("name", f"Browser {i+1}")
            
            # Wait for all to complete
            for future in as_completed(futures):
                browser_name = futures[future]
                try:
                    result = future.result()
                    print(f"\nCompleted: {result.get('browser', browser_name)}")
                except Exception as e:
                    print(f"\nError with {browser_name}: {e}")
        
        return self.results
    
    def print_summary(self):
        """Print summary of all BrowserStack results"""
        print("\n" + "="*80)
        print("BROWSERSTACK EXECUTION SUMMARY")
        print("="*80 + "\n")
        
        successful = 0
        failed = 0
        
        for result in self.results:
            status = "✓ SUCCESS" if result["success"] else "✗ FAILED"
            print(f"Browser: {result['browser']}")
            print(f"Status: {status}")
            print(f"Articles scraped: {result['articles_scraped']}")
            
            if result.get("repeated_words"):
                print(f"Repeated words found: {len(result['repeated_words'])}")
                for word, count in result["repeated_words"].items():
                    print(f"  - '{word}': {count}")
            
            if result.get("error"):
                print(f"Error: {result['error']}")
            
            print("-" * 40)
            
            if result["success"]:
                successful += 1
            else:
                failed += 1
        
        print(f"\nTotal: {len(self.results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")


def main():
    """
    Main function to run BrowserStack parallel execution
    """
    print("="*80)
    print("EL PAÍS WEB SCRAPING - BROWSERSTACK EXECUTION")
    print("="*80)
    
    # Check credentials
    if not BROWSERSTACK_USERNAME or not BROWSERSTACK_ACCESS_KEY:
        print("\nERROR: BrowserStack credentials not found!")
        print("Please set BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY environment variables")
        print("Or create a .env file with these credentials")
        return
    
    print(f"\nBrowserStack Username: {BROWSERSTACK_USERNAME}")
    print(f"Browsers to test: {len(BROWSERSTACK_BROWSERS)}")
    
    # Create runner
    runner = BrowserStackRunner()
    
    try:
        # Run parallel execution
        results = runner.run_parallel()
        
        # Print summary
        runner.print_summary()
        
    except Exception as e:
        print(f"\nError during BrowserStack execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
