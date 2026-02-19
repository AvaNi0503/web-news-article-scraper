# El País Web Scraping Project Plan

## Project Overview
Build a Selenium-based web scraping script that:
1. Scrapes articles from El País Opinion section
2. Downloads cover images
3. Translates titles to English
4. Analyzes repeated words in translated headers
5. Supports local and BrowserStack execution

## Files to Create

### 1. requirements.txt
- selenium
- webdriver-manager
- requests
- translate (or use rapid-translate-multi-traduction)

### 2. config.py
- BrowserStack credentials configuration
- Translation API settings
- El País URLs

### 3. scraper.py (Main Script)
- Selenium setup and teardown
- El País navigation
- Opinion section scraping
- Image download functionality

### 4. translator.py
- Translation API integration
- Translate article titles to English

### 5. text_analyzer.py
- Word frequency analysis
- Find words repeated more than twice

### 6. main.py
- Orchestrate all components
- Run locally first
- Run on BrowserStack with 5 parallel threads

### 7. browserstack_runner.py
- BrowserStack parallel execution setup
- Thread management for 5 browsers

### 8. .gitignore
- Ignore downloaded images, cache, etc.

## Technology Stack
- Language: Python
- Framework: Selenium WebDriver
- Translation API: Rapid Translate Multi Traduction API (free tier)
- Browser Automation: Chrome/Firefox locally, BrowserStack for cloud

## BrowserStack Configuration
- 5 parallel threads
- Mix of desktop and mobile browsers:
  1. Chrome (Windows 10)
  2. Firefox (Windows 10)
  3. Safari (macOS)
  4. Chrome (Android)
  5. Safari (iOS)

## Execution Steps
1. Install dependencies: pip install -r requirements.txt
2. Run locally: python main.py
3. Run on BrowserStack: python browserstack_runner.py
