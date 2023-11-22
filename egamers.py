from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import pandas as pd

class WebScraper:
    def __init__(self, url):
        self.driver = webdriver.Chrome()
        self.url = url

    def navigate(self):
        self.driver.get(self.url)


    def scrape_elements_by_class(self, class_name):
        # Find all elements with the parent class name
        elements = self.driver.find_elements(by=By.CLASS_NAME, value=class_name)

        # Iterate through the parent elements and find child elements within each one
        return elements
    
    def navigate_to_page(self, page_number):
        page_url = f'https://egamersworld.com/counterstrike/matches/history/page/{page_number}'
        self.driver.get(page_url)
    
    def scrape_all_pages(self, start_page=1, end_page=50):
        final_result = []  # List to store all match dictionaries

        # Iterate through the pages
        for page in range(start_page, end_page + 1):
            success = False  # Flag to check if the scraping was successful
            while not success:
                try:
                    print(f"Scraping page {page}...")
                    self.navigate_to_page(page)  # Navigate to the specific page
                    sleep(5)
                    result = self.scrape_matches()  # Scrape the matches on the current page
                    print(result)
                    # Add the scraped matches to the final result
                    for date, matches in result.items():
                        for match_dict in matches:
                            # Add date to match dictionary
                            match_dict['date'] = date
                            final_result.append(match_dict)
                    success = True  # If no exception occurred, set success to True
                except Exception as e:
                    print(f"An error occurred while scraping page {page}: {e}. Retrying...")
                    sleep(5)  # Wait for 5 seconds before retrying

        # Convert the final result to a Pandas DataFrame
        final_df = pd.DataFrame(final_result)

        return final_df



    def scrape_matches(self):
        # Find all match elements by the class name
        match_elements = self.driver.find_elements(by=By.ID, value='matches_finished')
        match_element = match_elements[0]
        matches = match_element.find_elements(by=By.CLASS_NAME, value='styles_matchBox__kc7rM.styles_withEvent__Sxvoe')
        # Initialize a dictionary to store the results
        results = {}

        for match in matches:
            if match is None:
                continue  # Skip if the match is None
            
            # Extracting the information
            details = match.text.split('\n')
            try:
                    
                if len(details) == 6: 
                    date_str = details[0]
                    date_object = datetime.strptime(date_str, "%d.%m.%y").date()
                    team1_name = details[1]
                    score = details[2].split(':')
                    match_format = details[3]
                    team2_name = details[4]
                    tournament_name = details[5]
                elif len(details) == 7:
                    date_str = details[1]
                    date_object = datetime.strptime(date_str, "%d.%m.%y").date()
                    team1_name = details[2]
                    score = details[3].split(':')
                    match_format = details[4]
                    team2_name = details[5]
                    tournament_name = details[6]
                else:
                    continue
            except:
                continue

            if score[0] > score[1]:
                winner = team1_name
            else:
                winner = team2_name
            # Constructing the match dictionary
            match_url = match.get_attribute('href')

            # Constructing the match dictionary
            match_dict = {
                'team1': team1_name,
                'team1_score': score[0],
                'team2': team2_name,
                'team2_score': score[1],
                'match_format': match_format,
                'tournament_name': tournament_name,
                'winner': winner,
                'match_url': match_url
            }

            # Adding the match dictionary to the results under the corresponding date
            if date_object not in results:
                results[date_object] = []
            results[date_object].append(match_dict)  # Appending match_dict, not DataFrame

        return results
        


    def wait_and_click_buttons(self):
        # Define the maximum wait time in seconds
        wait_time = 20

        # Define the class names for the two buttons
        button_class1 = 'styles_close__B5DYN'
        button_class2 = 'PopUpBannerClose'

        # Create a WebDriverWait instance
        wait = WebDriverWait(self.driver, wait_time)

        # Wait for the first button to become clickable and click it
        button1 = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, button_class1)))
        button1.click()

    def close(self):
        self.driver.close()
    
        
# Usage
url = 'https://egamersworld.com/counterstrike/matches/history'
scraper = WebScraper(url)
old_df =pd.read_csv('egamers_matches.csv', index_col=False)
scraper.navigate()
scraper.wait_and_click_buttons()
result = scraper.scrape_all_pages()
result = pd.concat([result, old_df])
result = result.drop_duplicates()
result.to_csv('egamers_matches.csv', index=False)
scraper.close()