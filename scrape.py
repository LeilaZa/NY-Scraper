#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 14 12:16:51 2021

@author: leila
"""
import time
import requests
from bs4 import BeautifulSoup
import json
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

base = "https://www.nytimes.com"
browser = webdriver.Chrome('/Users/leila/Downloads/chromedriver')
wait = WebDriverWait(browser, 10)
browser.get('https://www.nytimes.com/search?dropmab=false&endDate=20210119&query=%E2%80%9CSanctuary%20cities%E2%80%9D&sort=best&startDate=20180101&types=article')

while True:
    try:
        time.sleep(1)
        show_more = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@type="button"][contains(.,"Show More")]')))  
        show_more.click()
    except Exception as e:
            print(e)
            break    

soup = BeautifulSoup(browser.page_source,'lxml')
search_results = soup.find('ol', {'data-testid':'search-results'})

links = search_results.find_all('a')
with open('links.txt', 'w') as f:
    for link in links:
        f.write(str(link['href']))
        f.write("\n")


with open("NYnews.csv","w") as f:
    for link in links:
        link_url = link['href']
    
        #title = link.find('h4').text
        #date = link.find_next('time').text
        
        title = link.find('h4')
        try:
            date= link.find_all("span")[0].get_text().split("|")[1].split("Page")[0][:-2]
        except:
            if link.find_all("span"):
                date=link.find_all("span")[0].get_text().replace("PRINT EDITION", "")
                if ", Page" in date:
                    date = date[:date.index(", Page")]
            else:
                date=None
        
        if title is not None:
            title = title.text
        else:
            title = None
        
        try: 
            typeN= link['href'].split("/")[4]
        except:
            typeN=None
            
        try: 
            author= str(link).split("By")[1].split("<")[0]
        except:
            author=None
            
        #if date is not None:
       #     date = date.text
       # else:
        #    date = None
        print(str(date) + '\n'+ str(title) + '\n' + str(typeN) +
              '\n' + str(author)+
              '\n'+ str("https://www.nytimes.com")+ str(link['href']))
    
        response = requests.get(base + link_url)
        soup_link = BeautifulSoup(response.text, 'html.parser')
        scripts = soup_link.find_all('script')
        for script in scripts:
            if script.text is not None and 'window.__preloadedData = ' in script.text:
                jsonStr = script.text
                jsonStr = jsonStr.split('window.__preloadedData = ')[-1]
                jsonStr = jsonStr.rsplit(';',1)[0]
                
                try:
                    jsonData = json.loads(jsonStr)
                except:
                    continue
                article = []
                for k, v in jsonData['initialState'].items():
                    w=1
                    try:
                        if v['__typename'] == 'TextInline':
                            article.append(v['text'])
                            #print (v['text'])
                    except:
                        continue
                article = [ each.strip() for each in article ]
                article = ''.join([('' if c in string.punctuation else ' ')+c for c in article]).strip()
        print (article + '\n')
        
        f.write(str(date) + '\t'+ str(title) + '\t' + str(typeN) +
              '\t' + str(author)+
              '\t'+ str("https://www.nytimes.com")+ str(link['href'])+ '\t'+ article + '\n')

print("Complete")

browser.quit()