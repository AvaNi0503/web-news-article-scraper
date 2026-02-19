"""
Text Analysis module
Analyzes translated headers for repeated words
"""
import re
from collections import Counter


class TextAnalyzer:
    """Analyzer for finding repeated words in translated headers"""
    
    def __init__(self, min_repeat_count=2):
        """
        Initialize the analyzer
        
        Args:
            min_repeat_count: Minimum number of times a word must appear to be considered repeated
        """
        self.min_repeat_count = min_repeat_count
        self.word_counts = {}
        self.repeated_words = {}
    
    def clean_text(self, text):
        """
        Clean text by removing punctuation and converting to lowercase
        
        Args:
            text: Text to clean
            
        Returns:
            list: List of clean words
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation and special characters, keep only letters and spaces
        text = re.sub(r'[^a-z\s]', ' ', text)
        
        # Split into words and remove empty strings
        words = [word.strip() for word in text.split() if word.strip()]
        
        return words
    
    def count_words(self, titles):
        """
        Count word occurrences across all titles
        
        Args:
            titles: List of article titles
            
        Returns:
            dict: Dictionary of word counts
        """
        all_words = []
        
        for title in titles:
            words = self.clean_text(title)
            all_words.extend(words)
        
        # Count occurrences
        self.word_counts = Counter(all_words)
        
        return self.word_counts
    
    def find_repeated_words(self, titles):
        """
        Find words that appear more than twice across all titles
        
        Args:
            titles: List of article titles
            
        Returns:
            dict: Dictionary of words that appear more than twice with their counts
        """
        # Count all words
        self.count_words(titles)
        
        # Find words that appear more than min_repeat_count times
        # The task says "more than twice" = 3 or more times
        self.repeated_words = {
            word: count 
            for word, count in self.word_counts.items() 
            if count > self.min_repeat_count
        }
        
        return self.repeated_words
    
    def print_analysis(self, titles):
        """
        Print the word analysis results
        
        Args:
            titles: List of article titles to analyze
        """
        print(f"\n{'#'*80}")
        print("WORD FREQUENCY ANALYSIS")
        print(f"{'#'*80}\n")
        
        # First show all word counts
        print("All word counts (sorted by frequency):")
        print("-" * 40)
        
        word_counts = self.count_words(titles)
        
        # Sort by count descending
        sorted_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        for word, count in sorted_counts[:20]:  # Show top 20
            print(f"  {word}: {count}")
        
        # Now show repeated words (more than twice)
        print(f"\n{'='*60}")
        print("WORDS REPEATED MORE THAN TWICE")
        print(f"{'='*60}\n")
        
        repeated = self.find_repeated_words(titles)
        
        if repeated:
            # Sort by count descending
            sorted_repeated = sorted(repeated.items(), key=lambda x: x[1], reverse=True)
            
            print(f"Found {len(sorted_repeated)} words repeated more than twice:\n")
            
            for word, count in sorted_repeated:
                print(f"  '{word}' - {count} occurrences")
        else:
            print("No words found that appear more than twice.")
        
        print()
    
    def get_top_words(self, titles, n=10):
        """
        Get the top n most common words
        
        Args:
            titles: List of article titles
            n: Number of top words to return
            
        Returns:
            list: List of tuples (word, count)
        """
        word_counts = self.count_words(titles)
        return sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:n]


if __name__ == "__main__":
    # Test the analyzer
    analyzer = TextAnalyzer()
    
    test_titles = [
        "The Spanish Economy Grows More Than Expected",
        "The Government Presents New Infrastructure Plan",
        "Experts Warn About Climate Change",
        "New Technology Revolutionizes the Market",
        "Tourism in Spain Reaches Record Numbers"
    ]
    
    analyzer.print_analysis(test_titles)
