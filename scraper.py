from collections import defaultdict
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException

import google.auth
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build


SHEET_ID = "1wUA6T1R940Xt4cP3WWly3jdEwpcKsHQeI5v5oT2wPhw"
RANGE_NAME = 'Sheet1!A1:AU22'


def initialize_browser() -> webdriver.Chrome:
    """
    Initializes a Chrome browser instance with the specified options.

    Returns:
        browser (WebDriver): A WebDriver object representing the Chrome browser instance.
    """
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    browser = webdriver.Chrome(options=options)
    return browser


def login(browser: webdriver.Chrome) -> bool:
    """
    Logs in to the Therapeutic Research website using the provided browser.

    Args:
        browser (WebDriver): A WebDriver object representing the Chrome browser instance.
    """
   
    try:
        browser.get("https://naturalmedicines.therapeuticresearch.com/login?url=https%3a%2f%2fnaturalmedicines.therapeuticresearch.com%2f")
        username = browser.find_element(By.ID, "username")
        username.send_keys(open("login", "r").read() + Keys.RETURN)

        password = browser.find_element(By.ID, "password")
        password.send_keys(open("password", "r").read() + Keys.RETURN)
        return True
    except Exception as e:
        print(f"Error logging in: {e}")
        return False


def perform_searches(browser: webdriver.Chrome, interaction_map: dict) -> bool:
    """
    Performs searches for the elements in searches.txt. More or less a script that is executed to control the browser.

    Args:
        browser: An instance of the `webdriver.Chrome` class representing the web browser.

    Returns:
        interaction_map (dict): Contains all interactions for the medications, if they exist.
    """

    browser.get("https://naturalmedicines.therapeuticresearch.com/tools/interaction-checker.aspx")
    f = open("searches.txt", "r")
    searchterm = f.readline()

    # store interaction map for updating google spreadsheet later on
    interaction_map = defaultdict(list)
    success = True

    while searchterm and success:
        
        # failure to interact with browser elements is fatal, so break out of the loop
        try:
            browser.find_element(By.ID, "clearButton").click()
            search_box = browser.find_element(By.ID, "searchbox")
            search_box.send_keys(searchterm + Keys.RETURN)
            time.sleep(2)
        except ElementClickInterceptedException as e:
            frame = browser.find_element(By.XPATH, '//*[@id="hs-overlay-cta-127254074383"]/iframe')
            frame.send_keys(Keys.ESCAPE)
            continue
        
        except Exception as e:
             raise Exception(f"Unable to proceed: {e}")
        
        
        # a failure here is not fatal; just move on to the next term
        try:
            agent_message = browser.find_element(By.CLASS_NAME, "agentMessage")
            if "We could not find your product" in agent_message.text:
                print(f"Search term {searchterm} not found")
                searchterm = f.readline()
                continue
        except:
            pass
        
        try:
            view_results = browser.find_element(By.ID, "viewResultsButton")
            view_results.click()
            interactions = WebDriverWait(browser, 60).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "searchinteract")))
        except ElementClickInterceptedException as e:
        
            frame = browser.find_element(By.XPATH, '//*[@id="hs-overlay-cta-127254074383"]/iframe')
            frame.send_keys(Keys.ESCAPE)
            continue
        except Exception as e:
            raise Exception(f"Unable to proceed: {e}")
            
        
        # iterate through the scraped data, and store it in the interaction_map
        for i in interactions:
            other_thing = i.find_element(By.XPATH, ".//table/tbody/tr/td/table/tbody/tr/td[1]/span/b/a")
            
            try:
                interaction_severity = i.find_element(By.XPATH, './/table/tbody/tr/td/font/b').text
            except ElementClickInterceptedException as e:
                frame = browser.find_element(By.XPATH, '//*[@id="hs-overlay-cta-127254074383"]/iframe')
                frame.send_keys(Keys.ESCAPE)
                interaction_severity = i.find_element(By.XPATH, './/table/tbody/tr/td/font/b').text
            except Exception as e:
                raise Exception(f"Unable to proceed: {e}")
            
            interaction_msg = f'{searchterm} has a {interaction_severity} interaction with {other_thing.text}'
            interaction_map[searchterm].append(interaction_msg)

        searchterm = f.readline()
        time.sleep(5)

    f.close()

    return success

def generate_major_interactions(interactions: dict) -> dict:
    """
    Generates a dictionary of major interactions for each medication.

    Args:
        interactions (dict): All scraped drug interactions (minor, medium, major)

    Returns:
        major_interactions (dict): Contains a raw string to be uploaded to the spreadsheet for each major interaction
    """

    major_interactions = defaultdict(list)
    for k, v in interactions.items():
        k = k.split()[0]
        for i in v:
            if "Major" in i:
                words = i.split()
                other_thing = []
                for w in reversed(words):
                    if w == "with":
                        break
                    other_thing.append(w)
                other_thing = ' '.join(other_thing[::-1])
                major_interactions[k].append(f'{k} has a Major interaction with {other_thing}')

    return major_interactions


def get_spreadsheet_values(major_interactions: dict) -> list:
    """
    Retrieves values from Drug Nutrient Interaction spreadsheet using the Google Sheets API.

    Args:
        major_interactions (dict): A dictionary containing major interactions for drugs.

    Returns:
        list: A list of values retrieved from the spreadsheet.
    """
    try:
        creds, _ = google.auth.load_credentials_from_file('dfh-helper-key.json')
        sheets = build('sheets', 'v4', credentials=creds).spreadsheets()
        result = sheets.values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
        values = result.get('values', [])

        for i in range(len(values)):
            drugs = values[i][0].split()
            if len(values[i]) >= 12:
                values[i][10] = ''
            for d in drugs:
                if d in major_interactions and len(major_interactions[d]) > 0:
                    while len(values[i]) < 12:
                        values[i].append('')
                    values[i][10] = values[i][10] + '\n'.join(major_interactions[d]) + '\n'
                    values[i][11] = 'https://naturalmedicines.therapeuticresearch.com/tools/interaction-checker.aspx'

    except HttpError as err:
        raise Exception(f'Error ocurred: {err}')

    return values


def batch_update_values(spreadsheet_id, range_name, value_input_option, update_values):
    creds, _ = google.auth.load_credentials_from_file('dfh-helper-key.json')

    try:
        service = build('sheets', 'v4', credentials=creds)
        body = {
            'values': update_values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body
        ).execute()
        print(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        raise Exception(f'Error occurred: {error}')
    

if __name__ == '__main__':
    browser = initialize_browser()
    logged_in = login(browser)
    if not logged_in:
        raise Exception('Login failed')
    
    interaction_map = defaultdict(list)
    search_success = perform_searches(browser, interaction_map)

    if not search_success:
        raise Exception('Search failed')

    major_interactions = generate_major_interactions(interaction_map)
    spreadsheet_values = get_spreadsheet_values(major_interactions)
    batch_update_values(SHEET_ID, RANGE_NAME, 'USER_ENTERED', spreadsheet_values)

    browser.quit()