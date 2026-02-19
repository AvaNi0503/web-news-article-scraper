"""
Configuration file for El País Web Scraping Project
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# El País URLs
EL_PAIS_BASE_URL = "https://elpais.com"
EL_PAIS_OPINION_URL = "https://elpais.com/opinion/"

# BrowserStack Configuration
BROWSERSTACK_USERNAME = os.getenv("BROWSERSTACK_USERNAME", "")
BROWSERSTACK_ACCESS_KEY = os.getenv("BROWSERSTACK_ACCESS_KEY", "")

# Translation API Configuration
# Using Rapid Translate Multi Traduction API (free tier)
TRANSLATION_API_URL = "https://api.mymemory.translated.net/get"

# Local browser settings
LOCAL_BROWSER = "chrome"
LOCAL_HEADLESS = True  # Run in headless mode for local execution

# Download settings
IMAGE_DOWNLOAD_PATH = "./downloaded_images"
MAX_ARTICLES = 5

# BrowserStack browser configurations for parallel testing (5 threads)
BROWSERSTACK_BROWSERS = [
    {
        "browser": "Chrome",
        "browser_version": "latest",
        "os": "Windows",
        "os_version": "10",
        "name": "Chrome on Windows 10"
    },
    {
        "browser": "Firefox",
        "browser_version": "latest",
        "os": "Windows",
        "os_version": "10",
        "name": "Firefox on Windows 10"
    },
    {
        "browser": "Safari",
        "browser_version": "latest",
        "os": "OS X",
        "os_version": "Monterey",
        "name": "Safari on macOS"
    },
    {
        "browser": "Chrome",
        "browser_version": "latest",
        "os": "Android",
        "os_version": "11.0",
        "device": "Samsung Galaxy S21",
        "name": "Chrome on Android"
    },
    {
        "browser": "Safari",
        "browser_version": "latest",
        "os": "iOS",
        "os_version": "15.0",
        "device": "iPhone 13",
        "name": "Safari on iOS"
    }
]

# Selenium timeout settings
IMPLICIT_WAIT = 10
PAGE_LOAD_TIMEOUT = 30
SCRIPT_TIMEOUT = 30
