"""
El País Web Scraper using Selenium
Scrapes articles from the Opinion section
"""
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config import (
    EL_PAIS_OPINION_URL,
    IMAGE_DOWNLOAD_PATH,
    MAX_ARTICLES,
    LOCAL_HEADLESS,
    IMPLICIT_WAIT,
    PAGE_LOAD_TIMEOUT
)


class ElPaisScraper:
    """Scraper class for El País Opinion section"""
    
    def __init__(self, driver=None, is_browserstack=False):
        """
        Initialize the scraper
        
        Args:
            driver: Optional pre-configured driver. If None, creates local driver.
            is_browserstack: Whether using BrowserStack
        """
        self.driver = driver
        self.is_browserstack = is_browserstack
        self.articles = []
        
        # Create images directory if it doesn't exist
        if not os.path.exists(IMAGE_DOWNLOAD_PATH):
            os.makedirs(IMAGE_DOWNLOAD_PATH)
    
    def create_local_driver(self):
        """Create a local Chrome driver"""
        chrome_options = Options()
        if LOCAL_HEADLESS:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        # Set language to Spanish
        chrome_options.add_experimental_option("prefs", {"intl.accept_languages": "es"})
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(IMPLICIT_WAIT)
        self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
        
        return self.driver
    
    def navigate_to_opinion_section(self):
        """Navigate to El País Opinion section"""
        print(f"\n{'='*60}")
        print(f"Navigating to El País Opinion section...")
        print(f"{'='*60}")
        
        self.driver.get(EL_PAIS_OPINION_URL)
        
        # Wait for page to load
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "article"))
        )
        
        # Verify we're on the Spanish version
        html_lang = self.driver.find_element(By.TAG_NAME, "html").get_attribute("lang")
        print(f"Page language: {html_lang}")
        
        if "es" not in html_lang.lower():
            print("Warning: Page may not be in Spanish")
        
        time.sleep(2)  # Additional wait for content to load
    
    def get_article_links(self):
        """Get links to the first n articles in the Opinion section"""
        print(f"\nFetching first {MAX_ARTICLES} articles...")
        
        # First, try to find actual article links (not section pages)
        # Actual articles have patterns like: /YYYY/MM/DD/articulo-XXXX.html or contain /articulo/
        article_links = []
        seen_urls = set()
        
        # Try to find all links on the page first
        try:
            all_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='elpais.com']")
            print(f"Found {len(all_links)} total links on page")
            
            for link in all_links:
                try:
                    href = link.get_attribute("href")
                    if not href or href in seen_urls:
                        continue
                    
                    # Filter for actual article URLs (not section pages)
                    # Articles typically have patterns like:
                    # - /articulo/ in the URL
                    # - Date pattern like /2024/ or /2025/
                    # - End with .html
                    is_article = False
                    
                    # Check for article patterns
                    if "/articulo/" in href:
                        is_article = True
                    elif "/opinion/" in href and ("/2024/" in href or "/2025/" in href):
                        is_article = True
                    elif "/opinion/" in href and href.count("/") >= 5:  # More path segments = likely article
                        is_article = True
                    
                    # Exclude section pages
                    excluded_patterns = [
                        "/opinion/editoriales/",
                        "/opinion/tribunas/",
                        "/opinion/columnas/",
                        "/opinion/",  # Main opinion page
                        "/noticias/",  # News section
                    ]
                    
                    is_section = any(href.endswith(pattern) for pattern in excluded_patterns)
                    
                    if is_article and not is_section:
                        article_links.append(href)
                        seen_urls.add(href)
                        if len(article_links) >= MAX_ARTICLES:
                            break
                            
                except Exception:
                    continue
        except Exception as e:
            print(f"Error finding article links: {e}")
        
        # If no articles found with strict filtering, try broader approach
        if not article_links:
            print("No articles found with strict filtering, trying broader approach...")
            
            # Find article elements - El País uses different selectors
            article_selectors = [
                "article",
                ".article-card",
                ".headline-a",
                ".news-item",
                "[data-id*='article']"
            ]
            
            articles = []
            for selector in article_selectors:
                try:
                    articles = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(articles) >= MAX_ARTICLES:
                        print(f"Found {len(articles)} articles using selector: {selector}")
                        break
                except Exception as e:
                    print(f"Selector {selector} failed: {e}")
                    continue
            
            # Get unique article links - try to get href from article element or its children
            for article in articles:
                try:
                    # Try to get href directly from the article element
                    href = article.get_attribute("href")
                    
                    # If no href, try to find an anchor tag within the article
                    if not href:
                        try:
                            link_elem = article.find_element(By.CSS_SELECTOR, "a")
                            href = link_elem.get_attribute("href")
                        except Exception:
                            continue
                    
                    # Filter for valid URLs (allow any elpais.com article)
                    if href and href not in seen_urls and "elpais.com" in href:
                        article_links.append(href)
                        seen_urls.add(href)
                        if len(article_links) >= MAX_ARTICLES:
                            break
                except Exception:
                    continue
        
        print(f"Found {len(article_links)} article links to scrape")
        return article_links[:MAX_ARTICLES]
    
    def scrape_article(self, url):
        """
        Scrape individual article
        
        Args:
            url: Article URL
            
        Returns:
            dict: Article data with title, content, and image
        """
        print(f"\nScraping article: {url}")
        
        article_data = {
            "url": url,
            "title": "",
            "content": "",
            "image_url": "",
            "image_path": ""
        }
        
        try:
            self.driver.get(url)
            time.sleep(3)  # Wait for article to load
            
            # Get title - try multiple selectors
            title_selectors = [
                "h1",
                ".article-title",
                ".headline",
                "[class*='title']"
            ]
            
            for selector in title_selectors:
                try:
                    title_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    article_data["title"] = title_elem.text.strip()
                    if article_data["title"]:
                        break
                except Exception:
                    continue
            
            # Get content - try multiple selectors
            content_selectors = [
                ".article-text",
                ".article-body",
                "[class*='content']",
                "p"
            ]
            
            for selector in content_selectors:
                try:
                    paragraphs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    content_parts = [p.text.strip() for p in paragraphs if p.text.strip()]
                    if content_parts:
                        article_data["content"] = " ".join(content_parts[:10])  # First 10 paragraphs
                        break
                except Exception:
                    continue
            
            # Get cover image - try multiple selectors
            image_selectors = [
                "article img",
                ".article-image img",
                ".main-image img",
                "[class*='image'] img",
                "img.article"
            ]
            
            for selector in image_selectors:
                try:
                    img_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    img_url = img_elem.get_attribute("src") or img_elem.get_attribute("data-src")
                    if img_url:
                        article_data["image_url"] = img_url
                        break
                except Exception:
                    continue
            
            print(f"Title: {article_data['title'][:50]}...")
            print(f"Content length: {len(article_data['content'])} chars")
            print(f"Image URL: {article_data['image_url'][:50] if article_data['image_url'] else 'None'}...")
            
        except Exception as e:
            print(f"Error scraping article: {e}")
        
        return article_data
    
    def download_image(self, image_url, article_title, index):
        """
        Download and save article cover image
        
        Args:
            image_url: URL of the image
            article_title: Title of the article (for filename)
            index: Article index
            
        Returns:
            str: Path to saved image
        """
        if not image_url:
            return ""
        
        try:
            # Create safe filename from title
            safe_title = "".join(c for c in article_title[:30] if c.isalnum() or c in " -_").strip()
            safe_title = safe_title.replace(" ", "_")
            
            filename = f"article_{index+1}_{safe_title}.jpg"
            filepath = os.path.join(IMAGE_DOWNLOAD_PATH, filename)
            
            # Download image
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(image_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(response.content)
                print(f"Downloaded image: {filepath}")
                return filepath
            else:
                print(f"Failed to download image: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"Error downloading image: {e}")
        
        return ""
    
    def scrape_all_articles(self):
        """Main method to scrape all articles"""
        # Navigate to opinion section
        self.navigate_to_opinion_section()
        
        # Get article links
        article_links = self.get_article_links()
        
        if not article_links:
            print("No articles found!")
            return []
        
        print(f"\nFound {len(article_links)} articles to scrape")
        
        # Scrape each article
        for i, url in enumerate(article_links):
            print(f"\n{'='*60}")
            print(f"Article {i+1} of {len(article_links)}")
            print(f"{'='*60}")
            
            article_data = self.scrape_article(url)
            
            # Download image if available
            if article_data["image_url"]:
                article_data["image_path"] = self.download_image(
                    article_data["image_url"],
                    article_data["title"],
                    i
                )
            
            self.articles.append(article_data)
        
        return self.articles
    
    def print_articles(self):
        """Print all scraped articles"""
        print(f"\n{'#'*80}")
        print("SCRAPED ARTICLES")
        print(f"{'#'*80}\n")
        
        for i, article in enumerate(self.articles):
            print(f"\n{'='*60}")
            print(f"ARTICLE {i+1}")
            print(f"{'='*60}")
            print(f"Title: {article['title']}")
            print(f"\nContent (first 500 chars):\n{article['content'][:500]}...")
            print(f"\nImage: {article['image_path'] if article['image_path'] else 'Not available'}")
            print(f"URL: {article['url']}")
    
    def close(self):
        """Close the browser"""
        if self.driver and not self.is_browserstack:
            self.driver.quit()


def create_driver(is_browserstack=False, bs_config=None):
    """
    Create a Selenium WebDriver
    
    Args:
        is_browserstack: Whether to use BrowserStack
        bs_config: BrowserStack configuration dictionary
        
    Returns:
        WebDriver instance
    """
    if is_browserstack and bs_config:
        # BrowserStack driver setup
        from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
        from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
        
        # Build capabilities
        capabilities = {
            "browser": bs_config.get("browser", "Chrome"),
            "browser_version": bs_config.get("browser_version", "latest"),
            "os": bs_config.get("os", "Windows"),
            "os_version": bs_config.get("os_version", "10"),
            "resolution": "1920x1080",
            "browserstack.username": bs_config.get("username", ""),
            "browserstack.accessKey": bs_config.get("access_key", "")
        }
        
        # Add device info if present (mobile)
        if "device" in bs_config:
            capabilities["device"] = bs_config["device"]
        
        # Add Chrome options for language
        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", {"intl.accept_languages": "es"})
        
        # Build BrowserStack URL
        bs_url = f"https://{capabilities['browserstack.username']}:{capabilities['browserstack.accessKey']}@hub.browserstack.com/wd/hub"
        
        driver = RemoteWebDriver(command_executor=bs_url, options=chrome_options)
        driver.implicitly_wait(IMPLICIT_WAIT)
        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
        
        return driver
    else:
        # Local driver
        chrome_options = Options()
        if LOCAL_HEADLESS:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_experimental_option("prefs", {"intl.accept_languages": "es"})
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(IMPLICIT_WAIT)
        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
        
        return driver


if __name__ == "__main__":
    # Test the scraper locally
    scraper = ElPaisScraper()
    scraper.create_local_driver()
    
    try:
        articles = scraper.scrape_all_articles()
        scraper.print_articles()
    finally:
        scraper.close()
