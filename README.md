# Data Scraper

This project is a web scraping application built using Python and the Selenium library. It is designed to extract data from Otodom website and process that data for further analysis. 
For each apartment, the scraper collects:

- Type of market (primary or secondary)
- District (Warsaw district name)
- Price (total)
- Price (per m²)
- Area (in m²)
- Number of rooms
- Floor number


All numerical data is automatically cleaned and converted to appropriate formats for immediate use in data analysis.


## Installation

To set up the project, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd data-scraper
pip install -r requirements.txt
```

## Usage

To run the data scraper, execute the following command:

```bash
python main.py
```
## Adjust Settings
You can adjust the variable values according to the specific needs (you can find the current settings in the settings.py file).
For a quick test I scraped data of 50 apartments which took ~2-3 minutes.
Current settings are optimized for:

✅ Respectful scraping (won't harm the website)

✅ Avoiding detection/blocking

✅ Reasonable speed vs. safety balance

## Output Files
Files are saved in data/ with timestamps. Check the example file: warsaw_apartments_example.csv

## 📈 Use Cases
This dataset might be useful for:

### Basic Price Prediction Models

- Train ML models to predict apartment prices (requires time to scrape sufficient amount of data)
- Identify undervalued/overvalued properties
- Understand pricing factors (location, size, floor)


### Market Analysis

- Analyze price trends by district
- Calculate average price per m² by neighborhood
- Identify investment opportunities


### Data Visualization

- Create heatmaps of prices across Warsaw
- Visualize price distributions
- Compare districts


### Academic Research

- Real estate market studies
- Urban development analysis
- Economic research

