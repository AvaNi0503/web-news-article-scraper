# El País Opinion Scraper

A Python web scraping project that scrapes articles from the El País Opinion section, translates article titles to English, and analyzes the translated headers for repeated words.

## Features

- **Web Scraping**: Uses Selenium to scrape articles from El País Opinion section
- **Translation**: Translates article titles from Spanish to English using Google Translate API
- **Text Analysis**: Analyzes translated headers for repeated words
- **Image Download**: Downloads article cover images
- **Local & Cloud Testing**: Supports both local execution and BrowserStack parallel testing

## Requirements

- Python 3.8+
- Google Chrome browser
- ChromeDriver (automatically managed by webdriver-manager)

## Installation

1. Clone this repository:
```
bash
git clone https://github.com/yourusername/elpais-opinion-scraper.git
cd elpais-opinion-scraper
```

2. Install dependencies:
```
bash
pip install -r requirements.txt
```

## Usage

### Local Execution

Run the scraper locally:
```
bash
python main.py
```

This will:
1. Scrape 5 articles from El País Opinion section
2. Print article titles and content in Spanish
3. Download cover images (if available)
4. Translate article titles to English
5. Analyze translated headers for repeated words

### BrowserStack Execution

Run tests on BrowserStack with 5 parallel threads:
```
bash
python browserstack_runner.py
```

**Note**: Requires BrowserStack credentials set as environment variables:
- `BROWSERSTACK_USERNAME`
- `BROWSERSTACK_ACCESS_KEY`

Or create a `.env` file with these credentials.

## Project Structure

```
.
├── main.py                 # Local execution script
├── browserstack_runner.py # BrowserStack parallel execution
├── scraper.py             # Selenium web scraping module
├── translator.py          # Translation API module
├── text_analyzer.py      # Word frequency analysis
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore file
└── downloaded_images/   # Downloaded article images
```

## Configuration

Edit `config.py` to modify:
- Number of articles to scrape (`MAX_ARTICLES`)
- Headless mode (`LOCAL_HEADLESS`)
- Timeout settings
- BrowserStack browser configurations

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- El País for providing the content
- Selenium WebDriver for web automation
- Google Translate API for translation services
