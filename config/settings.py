class Settings:
    """Configuration for the scraper"""
    
    # Target URL
    OTODOM_URL = "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/mazowieckie/warszawa/warszawa/warszawa?limit=36&ownerTypeSingleSelect=PRIVATE&by=DEFAULT&direction=DESC"
    
    # Scraping limits
    MAX_APARTMENTS = 50
    MAX_PAGES = 3
    
    # Wait times (seconds)
    WAIT_BETWEEN_APARTMENTS = 2
    PAGE_LOAD_WAIT = 2
    
    # Browser settings
    HEADLESS = False
    
    # Output
    OUTPUT_FOLDER = "data"