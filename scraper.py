from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import re
from config.settings import Settings


class OtodomScraper:
    """Scraper for Otodom.pl apartments"""
    
    def __init__(self):
        """Initialize browser and settings"""
        self.apartments_data = []
        
        # Configure Chrome
        chrome_options = Options()
        if Settings.HEADLESS:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Start browser
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)

    def scrape(self):
        """
        Main scraping method.
        Returns: pd.DataFrame with apartment data
        """
        # Get apartment URLs from listing page
        apartment_urls = self._get_apartment_urls()
        
        if not apartment_urls:
            return pd.DataFrame()
        
        # Limit to MAX_APARTMENTS
        apartment_urls = apartment_urls[:Settings.MAX_APARTMENTS]
        
        # Scrape each apartment
        for i, url in enumerate(apartment_urls, 1):
            print(f"[{i}/{len(apartment_urls)}] Scraping apartment...")
            data = self._scrape_apartment(url)
            if data:
                self.apartments_data.append(data)
            time.sleep(Settings.WAIT_BETWEEN_APARTMENTS)
        
        # Convert to DataFrame and clean
        if not self.apartments_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.apartments_data)
        df = self._clean_dataframe(df)
        df = df.drop(columns=['price', 'price_per_m2', 'area_m2', 'rooms', 'floor', 'location', 'url'], errors='ignore')
        
        return df

    def _get_apartment_urls(self):
        """Get list of apartment URLs from listing page"""
        
        apartment_urls = []
        # Navigate through pages
        for page_num in range(1, Settings.MAX_PAGES + 1):
            print(f"Loading page {page_num}/{Settings.MAX_PAGES}...")
            
            # Construct page URL
            if page_num == 1:
                page_url = Settings.OTODOM_URL
            else:
                # Otodom adds &page=2, &page=3, etc.
                if '?' in Settings.OTODOM_URL:
                    page_url = f"{Settings.OTODOM_URL}&page={page_num}"
                else:
                    page_url = f"{Settings.OTODOM_URL}?page={page_num}"
            print(f"URL: {page_url}")

            # Navigate to page
            self.driver.get(page_url)
            time.sleep(Settings.PAGE_LOAD_WAIT)
            
            # Find all apartment links
            page_apartments = []
            try:
                link_elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/pl/oferta/"]')
                
                for element in link_elements:
                    try:
                        href = element.get_attribute('href')
                        if href and '/pl/oferta/' in href and '/pl/inwestycja/' not in href:
                            if href not in page_apartments:
                                page_apartments.append(href)
                    except Exception:
                        continue
                new_apartments = 0
                for href in page_apartments:
                    if href not in apartment_urls:
                        apartment_urls.append(href)
                        new_apartments += 1
                print(f"  Found {len(page_apartments)} apartments on page {page_num}")
                print(f"  New unique apartments: {new_apartments}")
                print(f"  Total collected: {len(apartment_urls)}")

                # Stop if we have enough apartments
                if len(apartment_urls) >= Settings.MAX_APARTMENTS:
                    print(f"Reached {Settings.MAX_APARTMENTS} apartments, stopping pagination")
                    break
                # Stop if no NEW apartments found (all were duplicates - reached the end)
                if new_apartments == 0:
                    print(f"\n✓ No new apartments on page {page_num}, reached end of listings")
                    break
            except Exception:
                print(f"Error on page {page_num}")
                continue
        
        return apartment_urls

    def _scrape_apartment(self, url):
        """Scrape single apartment page"""
        try:
            self.driver.get(url)
            time.sleep(Settings.PAGE_LOAD_WAIT)
            
            # Extract data
            data = {
                'rynek': self._get_detail_value('Rynek'),
                'price': self._get_price(),
                'price_per_m2': self._get_price_per_m2(),
                'area_m2': self._get_detail_value('Powierzchnia'),
                'rooms': self._get_detail_value('Liczba pokoi'),
                'floor': self._get_detail_value('Piętro'),
                'location': self._get_location(),
                'district': self._get_district(),
                'url': url
            }
            
            return data
        except Exception:
            return None
        

    def _get_price(self):
        """Get price from page using data-cy attribute"""
        try:
            # Use the specific data-cy attribute for price
            element = self.driver.find_element(By.CSS_SELECTOR, '[data-cy="adPageHeaderPrice"]')
            return element.text.strip()
        except Exception:
            return ""
    def _get_price_per_m2(self):
        """Get price per m2 from page using data-cy attribute"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, '[aria-label="Cena za metr kwadratowy"]')
            return element.text.strip()
        except Exception:
            return ""
        
    def _get_location(self):
        """Get location/address"""
        try:
            element = self.driver.find_element(By.XPATH, '//a[@href="#map"]')
            return element.text.strip()
        except Exception:
            return ""
        

    def _get_district(self):
        """Extract district name from location"""
        # List of all Warsaw districts (18 official districts)
        WARSAW_DISTRICTS = [
            'Bemowo', 'Białołęka', 'Bielany', 'Mokotów', 'Ochota',
            'Praga-Południe', 'Praga-Północ', 'Rembertów', 'Śródmieście',
            'Targówek', 'Ursus', 'Ursynów', 'Wawer', 'Wesoła',
            'Wilanów', 'Włochy', 'Wola', 'Żoliborz'
        ]
        
        try:
            location = self._get_location()
            if not location:
                return ""
            
            # Check each district name in the location string
            for district in WARSAW_DISTRICTS:
                if district.lower() in location.lower():
                    return district
            
            return ""
        except Exception:
            return ""
    
    def _get_detail_value(self, label):
        """Generic function to get any detail by its label"""
        try:
            # Find the label, then get the value div next to it
            xpath = f'//div[contains(text(), "{label}")]/following-sibling::div'
            element = self.driver.find_element(By.XPATH, xpath)
            return element.text.strip()
        except Exception:
            return ""
        

    def _clean_dataframe(self, df):
        """Clean DataFrame - convert text to numbers"""
        # Clean price
        if 'price' in df.columns:
            df['price_clean'] = df['price'].apply(self._extract_number)
        
        # Clean price per m2
        if 'price_per_m2' in df.columns:
            df['price_per_m2_clean'] = df['price_per_m2'].apply(self._extract_number)
        
        # Clean area
        if 'area_m2' in df.columns:
            df['area_clean'] = df['area_m2'].apply(self._extract_decimal)
        
        # Clean rooms
        if 'rooms' in df.columns:
            df['rooms_clean'] = df['rooms'].apply(self._extract_number)
        
        # Clean floor
        if 'floor' in df.columns:
            df['floor_clean'] = df['floor'].apply(self._extract_floor_number)
        
        return df

    def _extract_number(self, text):
        """Extract integer from text (e.g., "1 000 000 zł" -> 1000000)"""
        if pd.isna(text) or text == "":
            return None
        numbers = re.findall(r'\d+', str(text))
        if numbers:
            return int(''.join(numbers))
        return None

    def _extract_decimal(self, text):
        """Extract decimal from text (e.g., "45.5 m²" -> 45.5)"""
        if pd.isna(text) or text == "":
            return None
        numbers = re.findall(r'\d+\.?\d*', str(text).replace(',', '.'))
        if numbers:
            return float(numbers[0])
        return None

    def _extract_floor_number(self, text):
        """Extract floor number (parter = 0)"""
        if pd.isna(text) or text == "":
            return None
        
        text_lower = str(text).lower()
        if 'parter' in text_lower:
            return 0
        
        numbers = re.findall(r'\d+', text_lower)
        if numbers:
            return int(numbers[0])
        return None


    def save_to_csv(self, df, filename=None):
        """Save DataFrame to CSV"""
        import os
        from datetime import datetime
        
        os.makedirs(Settings.OUTPUT_FOLDER, exist_ok=True)
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f'warsaw_apartments_{timestamp}.csv'
        
        filepath = os.path.join(Settings.OUTPUT_FOLDER, filename)
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"Saved: {filepath}")


    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()