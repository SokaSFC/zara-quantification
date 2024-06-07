import os
import time
import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

now = datetime.datetime.now()
date_str = now.strftime('%d-%m-%Y')

data_dir = os.path.abspath("data")
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
    print('"data" directory created')

###################################   Scraping   ####################################

woman = "https://www.zara.com/ej/en/preowned-resell/products/woman-l1/new-in--l154"
man = "https://www.zara.com/ej/en/preowned-resell/products/man-l2/new-in--l151"
kid_1to14years = "https://www.zara.com/ej/en/preowned-resell/products/kids-l3/1-14-years-l2651"
kid_0to12months = "https://www.zara.com/ej/en/preowned-resell/products/kids-l3/0-12-months-l2650"


driver = webdriver.Chrome()
urls = [woman, man, kid_1to14years, kid_0to12months]


for url in urls:
    driver.get(url)
    print(url)

    print('Selecting filters')
    wait = WebDriverWait(driver, 10)
    filters_button = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'FILTERS')]")))
    filters_button.click()
    time.sleep(2)

    print('Click on "condition"')
    condition_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[.//span[contains(text(), 'condition')]]")))
    condition_button.click()
    time.sleep(2)

    conditions = ["New with tags", "Like new", "Good", "Fair"]

    for condition in conditions:

        print(f'Selecting "{condition}"')
        condition_button = wait.until(EC.presence_of_element_located((By.XPATH, f"//button[.//div[contains(text(), '{condition}')]]")))
        condition_button.click()
        time.sleep(2)

        if "kids" in url:
            age = url.split('/')[-1].split('-')[0]
            filename = os.path.join(data_dir, f"kid_{age}-{condition.lower().replace(' ', '_')}.html")
        else:
            filename = os.path.join(data_dir, f"{url.split('/')[-2]}-{condition.lower().replace(' ', '_')}.html")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            print(f'Page saved as "{filename}"')

        print(f'Unselecting "{condition}"')
        condition_button = wait.until(EC.presence_of_element_located((By.XPATH, f"//button[.//div[contains(text(), '{condition}')]]")))
        condition_button.click()
        time.sleep(2)

###################################   Parsing   ####################################

data = []

for filename in os.listdir(data_dir):
    if filename.endswith(".html"):
        parts = filename.split('-')
        gender = parts[0]
        condition = parts[-1]

        with open(os.path.join(data_dir, filename), "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, 'html.parser')

        button = soup.find('button', class_='zds-button filter__result-button zds-body-s zds-button--secondary')
        result_div = button.find('div', class_='zds-body-s')

        quantity = result_div.text.strip()

        data.append([gender, condition, quantity])

###################################   Cleaning   ####################################

df = pd.DataFrame(data, columns=['Gender', 'Condition', 'Quantity'])

df['Gender'] = df['Gender'].replace({'kid_1': '1to14', 'kid_0': '0to12'})

df['Condition'] = df['Condition'].str.replace('.html', '')

df['Quantity'] = df['Quantity'].str.extract('(\d+)').astype(int)

if not df.empty:
    df.to_csv(os.path.join(data_dir, f"quantification_{date_str}.csv"), index=False)
    print('DataFrame successfully exported')
else:
    print("Empty Data Frame, export aborted")
