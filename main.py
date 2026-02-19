"""
Main execution script for El País Web Scraping Project
Run locally to test functionality
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import ElPaisScraper, create_driver
from translator import Translator
from text_analyzer import TextAnalyzer
from config import MAX_ARTICLES


def main():
    """
    Main function to run the complete web scraping workflow
    """
    print("="*80)
    print("EL PAÍS WEB SCRAPING PROJECT")
    print("="*80)
    print("\nThis script will:")
    print(f"1. Scrape {MAX_ARTICLES} articles from El País Opinion section")
    print("2. Print article titles and content in Spanish")
    print("3. Download cover images (if available)")
    print("4. Translate article titles to English")
    print("5. Analyze translated headers for repeated words")
    print("="*80)
    
    # Step 1: Create scraper and driver
    print("\n[STEP 1] Setting up Selenium WebDriver...")
    driver = create_driver(is_browserstack=False)
    scraper = ElPaisScraper(driver=driver, is_browserstack=False)
    
    try:
        # Step 2: Scrape articles
        print("\n[STEP 2] Scraping articles from El País Opinion section...")
        articles = scraper.scrape_all_articles()
        
        if not articles:
            print("No articles found! Exiting.")
            return
        
        # Step 3: Print articles in Spanish
        print("\n[STEP 3] Displaying scraped articles (in Spanish)...")
        scraper.print_articles()
        
        # Step 4: Translate titles to English
        print("\n[STEP 4] Translating article titles to English...")
        
        # Get Spanish titles
        spanish_titles = [article["title"] for article in articles if article["title"]]
        
        # Translate titles
        translator = Translator()
        english_titles = translator.translate_titles(spanish_titles)
        
        # Print translated titles
        print("\n" + "="*60)
        print("TRANSLATED TITLES (English)")
        print("="*60)
        
        for i, (spanish, english) in enumerate(zip(spanish_titles, english_titles)):
            print(f"\nArticle {i+1}:")
            print(f"  Spanish: {spanish}")
            print(f"  English: {english}")
        
        # Step 5: Analyze translated headers
        print("\n[STEP 5] Analyzing translated headers for repeated words...")
        
        analyzer = TextAnalyzer(min_repeat_count=2)
        analyzer.print_analysis(english_titles)
        
        # Print summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total articles scraped: {len(articles)}")
        print(f"Articles with images: {sum(1 for a in articles if a['image_path'])}")
        print(f"Titles translated: {len(english_titles)}")
        
        # Show repeated words
        repeated = analyzer.find_repeated_words(english_titles)
        if repeated:
            print(f"\nRepeated words (appearing more than twice): {len(repeated)}")
            for word, count in sorted(repeated.items(), key=lambda x: x[1], reverse=True):
                print(f"  - '{word}': {count} times")
        else:
            print("\nNo words found that appear more than twice across all headers.")
        
        print("\n" + "="*80)
        print("EXECUTION COMPLETED SUCCESSFULLY")
        print("="*80)
        
    except Exception as e:
        print(f"\nError during execution: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up
        print("\nClosing browser...")
        scraper.close()


if __name__ == "__main__":
    main()
