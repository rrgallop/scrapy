# Therapeutic Research Interaction Checker

## Overview

This Python script utilizes the Selenium and Google Sheets API to automate interactions with the Therapeutic Research website's Interaction Checker tool. It performs searches for medications listed in the `searches.txt` file, retrieves drug interaction information, and updates a Google Spreadsheet with major interactions.

## Prerequisites

Before running the script, ensure you have the following:

- **Python:** Make sure you have Python installed on your system.
- **Chrome Browser:** The script uses the Chrome browser, so make sure it is installed.
- **WebDriver:** Download the ChromeDriver executable and ensure its location is in your system's PATH.
- **Google Sheets API Credentials:** Generate and download the API key file (`dfh-helper-key.json`) from the Google Cloud Console.
- **Google Sheets Spreadsheet:** Create a Google Spreadsheet with the specified `SHEET_ID` and `RANGE_NAME`.

## Installation

### 1. Clone the repository:

   ```bash
   git clone git@github.com:rrgallop/scrapy.git
   cd scrapy
   ```

### 2. If you haven't already installed `pipenv`, do so now.

    ```bash
    pip install pipenv
    ```

### 3. Create a virtual environment and install dependencies

    ```bash
    pipenv install selenium google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
    ```

### 4. API Key & Credentials

You will need `dfh-helper-key.json` in order to run this code on the spreadsheet I have provided. I can provide the API credentials file upon request.

### 5. Create Login and Password files

Create a `login` file containing just the login name for your website credentials. Similarly, create a `password` file with just the password for the account you would like to use. Place them in the base directory of your local `scrapy` repository. 

### 6. Populate searches.txt

Populate searches.txt with the names of the medications you would like to search for. It's important that you match the name of the medication *exactly* as it appears in the spreadsheet or the spreadsheet will fail to update.

### 7. Run the script

Run the script using:

```bash
pipenv run scrapy.py
```

A browser should open and you can watch the scraping process. Note, I have added delays to the scraping to reduce load on the target website. The script can execute in the background while you do something else.

### Conclusion

That's it! Please contact me directly with any questions.

-Ryan