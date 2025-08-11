"""
Enhanced web scraper with JavaScript rendering capabilities
Only searches for exact listener terms, no variations
"""
import logging
import time
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup
from models import AuctionItem

logger = logging.getLogger(__name__)

class WebScraper:
    """JavaScript-enabled web scraper"""
    
    def __init__(self):
        self.base_url = "https://live.aucor.com"
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with automatic driver management"""
        try:
            # Auto-install ChromeDriver
            chromedriver_autoinstaller.install()
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Chrome driver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Chrome driver: {e}")
            self.driver = None
            return False
    
    def scrape_auction_listings(self, search_terms=None):
        """
        Scrape auction listings using exact search terms only (no variations)
        """
        if not self.driver:
            logger.error("Driver not available")
            return []
        
        if not search_terms:
            logger.warning("No search terms provided")
            return []
        
        all_items = []
        
        # Use exact search terms only, no variations
        for search_term in search_terms:
            logger.info(f"🔍 Searching Aucor for EXACT term: '{search_term}'")
            items = self._scrape_for_term(search_term.strip())
            all_items.extend(items)
        
        # Remove duplicates based on URL
        unique_items = []
        seen_urls = set()
        
        for item in all_items:
            if item.url not in seen_urls:
                unique_items.append(item)
                seen_urls.add(item.url)
        
        logger.info(f"🎯 Found {len(unique_items)} unique auction items")
        return unique_items
    
    def _scrape_for_term(self, search_term):
        """Scrape for a specific exact search term"""
        search_url = f"{self.base_url}/lots?search={search_term.replace(' ', '+')}&lots_range=upcoming"
        
        try:
            logger.info(f"📡 Loading: {search_url}")
            self.driver.get(search_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Wait for content to appear
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                logger.info("✅ Page loaded completely")
            except TimeoutException:
                logger.warning("⚠️ Page load timeout, proceeding anyway")
            
            # Additional wait for dynamic content
            time.sleep(2)
            
            # Get page source after JavaScript execution
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Check if we have real content or template data
            if self._is_template_page(soup):
                logger.warning(f"⚠️ Page appears to contain template data for term: {search_term}")
                return []
            
            # Extract auction items
            items = self._extract_auction_items(soup, search_url)
            
            logger.info(f"📦 Found {len(items)} items for term: {search_term}")
            return items
            
        except WebDriverException as e:
            logger.error(f"❌ WebDriver error for term '{search_term}': {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Unexpected error for term '{search_term}': {e}")
            return []
    
    def _is_template_page(self, soup):
        """Check if the page contains only template/placeholder data"""
        page_text = soup.get_text().lower()
        
        # Check for template indicators
        template_indicators = [
            'no lots found',
            'no auctions found',
            'coming soon',
            'page not found',
            'javascript:void(0)'
        ]
        
        # Check if page is mostly template
        if any(indicator in page_text for indicator in template_indicators):
            return True
        
        # Check if page has very little content
        meaningful_text = soup.get_text(strip=True)
        if len(meaningful_text) < 100:
            return True
            
        return False
    
    def _extract_auction_items(self, soup, source_url):
        """Extract auction items from the page"""
        items = []
        
        # Try multiple selectors to find auction items
        auction_selectors = [
            '[data-testid*="lot"]',
            '[data-testid*="item"]',
            '.lot-item',
            '.auction-item',
            '.item-card',
            '[class*="lot-"]',
            '[class*="item-"]',
            '.card',
            '.listing'
        ]
        
        auction_elements = []
        
        for selector in auction_selectors:
            elements = soup.select(selector)
            if elements:
                logger.info(f"🎯 Found {len(elements)} elements with selector: {selector}")
                auction_elements = elements
                break
        
        if not auction_elements:
            # Fallback: look for any links that might be auction items
            logger.info("🔍 No structured elements found, trying link fallback")
            auction_elements = soup.find_all('a', href=True)
            auction_elements = [elem for elem in auction_elements if self._looks_like_auction_link(elem)]
        
        # Extract data from found elements
        for elem in auction_elements[:20]:  # Limit to 20 items per search
            item = self._extract_item_data(elem, source_url)
            if item:
                items.append(item)
        
        return items
    
    def _looks_like_auction_link(self, elem):
        """Check if an element looks like an auction item link"""
        href = elem.get('href', '').lower()
        text = elem.get_text(strip=True).lower()
        
        # Skip navigation, template, and common UI elements
        skip_indicators = [
            'javascript:void(0)',
            'login', 'register', 'sign in', 'sign up',
            'quick bid', 'bid now', 'place bid',
            'home', 'about', 'contact', 'help',
            'browse', 'search', 'filter'
        ]
        
        if any(indicator in href or indicator in text for indicator in skip_indicators):
            return False
        
        # Look for auction-like indicators
        auction_indicators = [
            'lot', 'item', 'auction', 'details',
            'view', 'show'
        ]
        
        return any(indicator in href for indicator in auction_indicators) and len(text) > 5
    
    def _extract_item_data(self, elem, source_url):
        """Extract auction item data from an element"""
        try:
            # Extract title
            title = self._extract_title(elem)
            if not title:
                return None
            
            # Skip template/placeholder titles
            if title.lower() in ['quick bid', 'bid now', 'place bid', 'login', 'register', 'search', 'browse']:
                logger.debug(f"⏭️ Skipping template title: {title}")
                return None
            
            # Skip obviously fake/mock titles
            if 'mock' in title.lower() or 'test' in title.lower():
                logger.debug(f"⏭️ Skipping mock/test title: {title}")
                return None
            
            # Extract URL
            url = self._extract_url(elem)
            if 'javascript:void(0)' in url:
                logger.debug(f"⏭️ Skipping JavaScript void URL for: {title}")
                return None
            
            # Extract other data
            price = self._extract_price(elem)
            description = self._extract_description(elem)
            
            # Create auction item
            item = AuctionItem(
                title=title,
                url=url,
                price=price,
                description=description,
                end_time="",
                image_url=""
            )
            
            logger.info(f"✅ Extracted item: {title}")
            return item
            
        except Exception as e:
            logger.warning(f"⚠️ Error extracting item data: {e}")
            return None
    
    def _extract_title(self, elem):
        """Extract title from element"""
        # Try different title extraction methods
        title_methods = [
            lambda: elem.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']),
            lambda: elem.find(class_=lambda x: x and 'title' in x.lower()),
            lambda: elem.find(['strong', 'b']),
            lambda: elem.find('span'),
            lambda: elem if elem.name == 'a' else None
        ]
        
        for method in title_methods:
            try:
                title_elem = method()
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) > 3:
                        return title
            except:
                continue
        
        return None
    
    def _extract_url(self, elem):
        """Extract URL from element"""
        if elem.name == 'a':
            href = elem.get('href', '')
        else:
            link = elem.find('a')
            href = link.get('href', '') if link else ''
        
        if href:
            if not href.startswith('http'):
                if href.startswith('/'):
                    href = f"{self.base_url}{href}"
                else:
                    href = f"{self.base_url}/{href}"
        
        return href
    
    def _extract_price(self, elem):
        """Extract price from element"""
        price_patterns = ['price', 'bid', 'amount', 'cost', 'value']
        
        for pattern in price_patterns:
            price_elem = elem.find(class_=lambda x: x and pattern in x.lower())
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                if price_text and any(char.isdigit() for char in price_text):
                    return price_text
        
        return ""
    
    def _extract_description(self, elem):
        """Extract description from element"""
        # Get element text, but limit length
        text = elem.get_text(strip=True)
        return text[:200] if text else ""
    
    def get_new_items(self):
        """Get new auction items that haven't been processed yet"""
        from models import Listener
        
        try:
            listeners = Listener.get_all()
            if listeners:
                # Use exact search terms from listeners (no variations)
                search_terms = [listener.search_term for listener in listeners]
                logger.info(f"🎯 Using EXACT search terms from {len(listeners)} listeners: {search_terms}")
                
                all_items = self.scrape_auction_listings(search_terms)
            else:
                logger.warning("No active listeners found")
                return []
                
        except Exception as e:
            logger.error(f"Error getting listeners: {e}")
            return []
        
        new_items = []
        
        for item in all_items:
            # Check if URL already exists in database
            if not AuctionItem.url_exists(item.url):
                if item.save():
                    new_items.append(item)
                    logger.info(f"💾 Saved new auction item: {item.title}")
        
        logger.info(f"🎉 Found {len(new_items)} new auction items")
        return new_items
    
    def close(self):
        """Clean up the driver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("🔒 Chrome driver closed")
            except:
                pass
    
    def __del__(self):
        """Ensure driver is closed when object is destroyed"""
        self.close()
