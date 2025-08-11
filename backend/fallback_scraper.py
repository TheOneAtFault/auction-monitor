"""
Fallback scraper using basic HTTP requests (no JavaScript)
"""
import requests
from bs4 import BeautifulSoup
import time
import random
from models import AuctionItem
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FallbackScraper:
    """Fallback scraper using basic HTTP requests"""
    
    def __init__(self):
        self.base_url = "https://live.aucor.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://live.aucor.com/'
        })
    
    def scrape_auction_listings(self, search_terms=None):
        """Basic scraping - fallback when Selenium not available"""
        logger.warning("Using basic HTTP scraper - JavaScript content may not be available")
        
        if not search_terms:
            logger.warning("No search terms provided")
            return []
        
        all_items = []
        
        for term in search_terms:
            logger.info(f"Basic search for exact term: '{term}'")
            items = self._search_basic(term)
            all_items.extend(items)
        
        return self._filter_and_deduplicate(all_items)
    
    def _search_basic(self, search_term):
        """Basic search without JavaScript rendering"""
        search_url = f"{self.base_url}/lots?search={search_term.replace(' ', '+')}&lots_range=upcoming"
        
        try:
            time.sleep(random.uniform(1, 2))  # Be respectful
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                return self._extract_basic_items(soup, search_url)
            else:
                logger.warning(f"HTTP {response.status_code} for term: {search_term}")
                return []
                
        except Exception as e:
            logger.warning(f"Basic search failed for '{search_term}': {e}")
            return []
    
    def _extract_basic_items(self, soup, source_url):
        """Extract items using basic HTML parsing"""
        items = []
        
        # Look for any links that might be auction items
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Filter out template/navigation links
            if (self._is_auction_link(href, text) and 
                not self._is_template_content(text)):
                
                item = self._create_auction_item(text, href, source_url)
                if item:
                    items.append(item)
        
        logger.info(f"Basic extraction found {len(items)} potential items")
        return items[:10]  # Limit results
    
    def _is_auction_link(self, href, text):
        """Check if link appears to be an auction item"""
        auction_indicators = ['/lots/', '/item/', '/auction/']
        return (any(indicator in href for indicator in auction_indicators) and
                len(text) > 5 and
                'javascript:void(0)' not in href)
    
    def _is_template_content(self, text):
        """Check if text is template/placeholder content"""
        template_terms = [
            'quick bid', 'bid now', 'place bid', 'login', 'register',
            'sign in', 'sign up', 'browse', 'search', 'home', 'about'
        ]
        return text.lower() in template_terms
    
    def _create_auction_item(self, title, url, source_url):
        """Create an AuctionItem from basic data"""
        try:
            # Make URL absolute
            if not url.startswith('http'):
                if url.startswith('/'):
                    url = f"{self.base_url}{url}"
                else:
                    url = f"{self.base_url}/{url}"
            
            return AuctionItem(
                title=title[:100],  # Truncate long titles
                url=url,
                description=title,
                price="",
                end_time="",
                image_url=""
            )
        except Exception as e:
            logger.warning(f"Error creating auction item: {e}")
            return None
    
    def _filter_and_deduplicate(self, items):
        """Remove duplicates and filter invalid items"""
        unique_items = []
        seen_urls = set()
        
        for item in items:
            if item and item.url not in seen_urls:
                unique_items.append(item)
                seen_urls.add(item.url)
        
        logger.info(f"After deduplication: {len(unique_items)} unique items")
        return unique_items
    
    def get_new_items(self):
        """Get new auction items that haven't been processed yet"""
        from models import Listener
        
        try:
            listeners = Listener.get_all()
            if listeners:
                search_terms = [listener.search_term for listener in listeners]
                logger.info(f"Basic scraper using exact terms: {search_terms}")
                all_items = self.scrape_auction_listings(search_terms)
            else:
                logger.warning("No active listeners found")
                return []
                
        except Exception as e:
            logger.error(f"Error getting listeners: {e}")
            return []
        
        new_items = []
        
        for item in all_items:
            if not AuctionItem.url_exists(item.url):
                if item.save():
                    new_items.append(item)
                    logger.info(f"Saved new item (basic): {item.title}")
        
        logger.info(f"Basic scraper found {len(new_items)} new items")
        return new_items

def match_search_terms(item, search_terms):
    """Check if an auction item matches any of the given search terms"""
    item_text = f"{item.title} {item.description}".lower()
    
    matches = []
    for term in search_terms:
        if term.lower() in item_text:
            matches.append(term)
    
    return matches
