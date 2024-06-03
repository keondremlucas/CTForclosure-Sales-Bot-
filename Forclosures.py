from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import time

def get_foreclosure_data(date_to_check):
    # Set up Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    url = 'https://sso.eservices.jud.ct.gov/foreclosures/Public/PendPostbyTownList.aspx'
    driver.get(url)
    
    # Wait until the town links are present
    try:
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href^="Public/PendPostbyTown.aspx?Town="]'))
    except Exception as e:
        print(f"Error waiting for town links: {e}")
        driver.quit()
        return {}
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    town_links = soup.find_all('a')
    filtered_array =[tag['href'].split('=')[1] for tag in town_links if '=' in tag.get('href', '')]
    print("Towns:: ",filtered_array)
    if not filtered_array:
        print("No town links found.")
        driver.quit()
        return {}
    
    towns_with_matches = {}
    for link in filtered_array:
        town_url = f"https://sso.eservices.jud.ct.gov/foreclosures/Public/PendPostbyTownDetails.aspx?town={link}"
        
        driver.get(town_url)
        url = town_url
        # Wait until the sale dates are present
    
        town_soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        date_pattern = re.compile(r'\d{2}-\d{2}-\d{4}.*?(\d{2}:\d{2} [AP]M)')
        
        spans_with_ct100 = town_soup.find_all(lambda tag: tag.name == 'span' and 'Label1' in tag.get('id', ''))
        sale_dates = [span.text[:10] for span in spans_with_ct100]
        
        sale_count = 0
        for sale_date in sale_dates:
            if sale_date == date_to_check:
                sale_count += 1
        
        if sale_count > 0:
            towns_with_matches[link] = {'count':sale_count, 'url': town_url}
    
    driver.quit()
    return towns_with_matches

# Get user input for date
date_to_check = input("Enter a date (MM/DD/YYYY) to check for foreclosure sales: ")
matches = get_foreclosure_data(date_to_check)
# Print results
print('')
print('')
if matches:
    for town, info in matches.items():
        
        print(f"{town}: {info['count']} sale(s) on {date_to_check} - {info['url']}")
else:
    print(f"No towns have sales on {date_to_check}")