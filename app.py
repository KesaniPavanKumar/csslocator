#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 17:37:27 2024

@author: kesanipavankumar
"""

from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")
from selenium.webdriver.common.by import By
import time
from io import BytesIO
from PIL import Image
import pytesseract
import pandas as pd
from undetected_chromedriver import Chrome, ChromeOptions


from sqlalchemy import create_engine, inspect
from urllib.parse import quote_plus

import warnings
warnings.filterwarnings("ignore")



app = Flask(__name__)

pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

db_credentials = {
    'user': 'postgres',
    'password': '123',
    'host': 'localhost',
    'port': '5432',
    'database': 'postgres',
}

def connect_and_insert_data(data, table_name, db_credentials):
    df = pd.DataFrame(data)
    encoded_password = quote_plus(db_credentials['password'])
    conn_string = f"postgresql+psycopg2://{db_credentials['user']}:{encoded_password}@{db_credentials['host']}:{db_credentials['port']}/{db_credentials['database']}"
    engine = create_engine(conn_string)

    # Check if the table exists using inspect
    inspector = inspect(engine)
    table_exists = inspector.has_table(table_name)

    # If the table exists, append data; otherwise, create the table
    if table_exists:
        df.to_sql(table_name, engine, if_exists='append', index=False)
    else:
        df.to_sql(table_name, engine, if_exists='replace', index=False)

    engine.dispose()
    
    return 'success'


def img_text(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    text = pytesseract.image_to_string(img)
    return text

def selectdropdown(ID, data, driver):
    element = driver.find_element(By.ID, ID)
    element.send_keys(data)
    return "success"

def scrape_data(driver):
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        states = soup.find('select', attrs={'id': 'state'}).find_all('option')
        states_list = [state.text for state in states if state.text != 'Select State']
        data_collection = []

        for state in states_list[0:1]:
            selectdropdown('state', state, driver)
            time.sleep(2)

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            cities = soup.find('select', attrs={'id': 'district'}).find_all('option')
            cities_list = [city.text for city in cities if city.text != 'Select District']

            for city in cities_list[0:1]:
                selectdropdown('district', city, driver)
                time.sleep(2)

                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                branches = soup.find('select', attrs={'id': 'block'}).find_all('option')
                branches_list = [branch.text for branch in branches if branch.text != 'Select Block']
                
                if (len(branches_list) != 0):
                    for branch in branches_list[0:]:
                        try:
                            selectdropdown('block', branch, driver)
                            time.sleep(2)
    
                            html = driver.page_source
                            soup = BeautifulSoup(html, 'html.parser')
    
                            tables = soup.find_all('table')
                            table = tables[0]
     
                            rows = table.find_all('tr')
                            for row in rows:
                                try:
                                    data_dict = {}
                                    cells = row.find_all('td') 
                                    
                                    if (len(cells) != 0):
                                        
                                        # data_dict['location'] = state+','+ city + ','+branch
                                        data_dict['Name'] = cells[0].text
                                        data_dict['Address'] = cells[1].text
                                        
                                        data_url = cells[2].a['href']
                                        
                                        
                                        data=requests.get(data_url)
                                        soup = BeautifulSoup(data.text, 'html.parser')
    
                                        Img_Num = soup.select_one('body > div:nth-of-type(1) > div:nth-of-type(3) > div:nth-of-type(1) > div > article > div > div > img')['src']
                                        
                                        
                                        data_dict['Phone No.'] = img_text(Img_Num).replace("\n", "")
                                        print(data_dict)
                                        data_collection.append(data_dict)
                                   
                                except Exception as e:
                                    print("try ====== row iteratior error")
                                    print(e)
                                    pass
    
                        except Exception as e:
                            print(e)
                            return [e]
        
        connect_and_insert_data(data=data_collection, table_name='csslocator', db_credentials=db_credentials)

        # Convert data to DataFrame
        df = pd.DataFrame(data_collection)
        
        # Convert DataFrame to CSV
        csv_filename = 'output_data.csv'
        df.to_csv(csv_filename, index=False)
                
        return data_collection

    except Exception as e:
        print(e)
        return [e]
 
    finally:
        pass
        driver.quit()

@app.route('/get_css_locator_data', methods=['GET'])
def get_data():
    try:
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless")
        driver = Chrome(options=chrome_options)
        # driver = uc.Chrome()
        driver.get('https://www.csclocator.com/csc')
        data = scrape_data(driver)
        print(data)
        return jsonify({"status": "success", "data": data})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
