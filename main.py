from scraper import OtodomScraper

def main():
    """Run the scraper"""
    
    scraper = OtodomScraper()
    
    try:
        # Scrape apartments
        df = scraper.scrape()
        
        if df.empty:
            print("No data collected")
            return
        
        # Show results
        print(f"\nScraped {len(df)} apartments")
        print(df.head())
        
        
        # Save
        scraper.save_to_csv(df)
        
        return df
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        scraper.close()


if __name__ == "__main__":
    df = main()