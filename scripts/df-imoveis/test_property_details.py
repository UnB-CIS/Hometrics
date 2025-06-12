import os
import pandas as pd
import requests
from bs4 import BeautifulSoup


# Define headers for requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0'
}

def test_property_details_scraper(category='venda', tsv_filename=None, delay=2):
    """Test function for scraping the first property from a TSV file and showing the raw HTML"""
    
    # If no tsv_filename is provided, use the default naming pattern
    if tsv_filename is None:
        tsv_filename = f'imoveis_df_{category}.tsv'
    
    # Construct the full path to the TSV file
    tsv_file_path = os.path.join("scripts/df-imoveis/dataset/raw_listings", tsv_filename)
    
    # Verify the file exists
    if not os.path.exists(tsv_file_path):
        print(f"Error: TSV file not found at {tsv_file_path}")
        return
    
    print(f"Reading first property from {tsv_file_path}")
    
    try:
        # Read just the first line
        df = pd.read_csv(tsv_file_path, sep='\t', nrows=1)
        
        if df.empty:
            print("No properties found in the TSV file.")
            return
        
        first_url = df.iloc[0, 0]
        print(f"Fetching URL: {first_url}")
        response = requests.get(first_url, headers=HEADERS)
        
        if response.status_code == 200:
            # Parse the HTML content
            property_soup = BeautifulSoup(response.text, "html.parser")

            properties = property_soup.find_all('p', class_='texto-descricao')
            
            
            # Print the BeautifulSoup parsed HTML
            print("\nBeautifulSoup parsed HTML:")
            print(properties)

            
            print(f"\n==============================================")
            print(f"URL FOR MANUAL CHECKING: {first_url}")
            print(f"==============================================")

            
        else:
            print(f"Failed to fetch property page. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error processing TSV file: {str(e)}")

if __name__ == "__main__":
    # Change these parameters as needed
    test_property_details_scraper(
        category='venda',
        delay=2  # Delay between requests in seconds
    )
