from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

LOGIN = ""
PASSWORD = ""
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
browser = webdriver.Chrome(options=options)
browser.get("https://naturalmedicines.therapeuticresearch.com/login?url=https%3a%2f%2fnaturalmedicines.therapeuticresearch.com%2f")
username = browser.find_element(By.ID, "username")
username.send_keys(LOGIN + Keys.RETURN)
password = browser.find_element(By.ID, "password")
password.send_keys(PASSWORD + Keys.RETURN)
# browser.quit()
browser.get("https://naturalmedicines.therapeuticresearch.com/tools/interaction-checker.aspx")

"""
Fluorouracil
Fluorouracil
Fluorouracil
Fluoxetine
Fluticasone
Fluticasone
Salmeterol
Fluticasone
Vilanterol
Fluvastatin
Fluvoxamine
Furosemide
Gabapentin
Gemcitabine
Glimepiride
Glipizide
Hydrochlorothiazide
Hydrochlorothiazide
Lisinopril
Hydroxychloroquine
Hydroxyzine
Ibuprofen
Imipramine
Indomethacin
"""
# head-standard-button-dark https://naturalmedicines.therapeuticresearch.com/login?url=https%3a%2f%2fnaturalmedicines.therapeuticresearch.com%2f