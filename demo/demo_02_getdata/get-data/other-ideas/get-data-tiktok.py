
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options  
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.touch_actions import TouchActions

import time
from datetime import datetime
import json


# specify script variables
tiktoks = []
time_interval = 5
start_timestamp = datetime.now()
start = True

while True:

    # every X minutes (according to the time interval) reset the browser and save the results to the file
    current_timestamp = datetime.now()
    duration = int(((current_timestamp - start_timestamp).seconds)/60)

    if start == True or (duration % time_interval == 0 and duration != 0):

        # save current tiktoks to the file
        if start == False:

            # save the file
            file_name = f"tiktoks_{datetime.today().strftime('%Y%m%d_%H%M%S')}.json"
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(tiktoks, f, ensure_ascii=True, indent=4)
            print(f"saving file: {file_name}")

            # maintanance, reset start timestamp and clear the tiktok list, also close browser
            start_timestamp = current_timestamp
            tiktoks.clear()
            browser.close()

        else:
            start = False

        # initialize        
        chrome_options = Options()
        chrome_options.add_argument("user-agent=Googlebot")
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=2')
        browser = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=chrome_options)

        # load main page and wait 2 seconds
        base_url = "https://www.tiktok.com"
        browser.get(base_url)
        time.sleep(2)

        # accept cookie button
        accept_cookie_button = browser.find_element_by_xpath('//button[text()="Accept all"]')
        accept_cookie_button.click()
        time.sleep(2)

        

    # get all avaliable tiktoks from the page
    tiktok_entries = browser.find_elements_by_xpath("//span[@class='lazyload-wrapper']")
    print(f"found {len(tiktok_entries)} tiktoks")

    # iterate through each tiktok
    for tiktok_entry in tiktok_entries:

        try:

            # get needed information from each tiktok
            tiktok_bottom_authorname = tiktok_entry.find_element_by_xpath(".//div[contains(@class, 'author-info-content tt-author-info')]//h3[contains(@class, 'author-uniqueId')]").text
            tiktok_bottom_authornickname = tiktok_entry.find_element_by_xpath(".//div[contains(@class, 'author-info-content tt-author-info')]//h4[contains(@class, 'author-nickname')]").text
            tiktok_bottom_authorlink = tiktok_entry.find_element_by_xpath(".//div[contains(@class, 'author-info-content tt-author-info')]//a").get_attribute('href')
            tiktok_bottom_hashtags = [hashtag.text for hashtag in tiktok_entry.find_elements_by_xpath(".//div[contains(@class, 'tt-video-meta-caption')]//a//strong")]
            tiktok_bottom_soundtrack = tiktok_entry.find_element_by_xpath(".//div[contains(@class, 'music-title-decoration')]").text
            tiktok_bottom_likes = tiktok_entry.find_element_by_xpath(".//div[contains(@class, 'item-action-bar vertical')]//div[contains(@class, 'bar-item-wrapper')]//strong[@title='like']").text
            tiktok_bottom_comments = tiktok_entry.find_element_by_xpath(".//div[contains(@class, 'item-action-bar vertical')]//div[contains(@class, 'bar-item-wrapper')]//strong[@title='comment']").text
            tiktok_bottom_shares = tiktok_entry.find_element_by_xpath(".//div[contains(@class, 'item-action-bar vertical')]//div[contains(@class, 'bar-item-wrapper')]//strong[@title='share']").text

            # save tiktok information to the dictionary entry and add to the list
            tiktok = {}
            tiktok['authorname'] = tiktok_bottom_authorname
            tiktok['authornickname'] = tiktok_bottom_authornickname
            tiktok['hashtags'] = tiktok_bottom_hashtags
            tiktok['soundtrack'] = tiktok_bottom_soundtrack
            tiktok['likes'] = tiktok_bottom_likes
            tiktok['comments'] = tiktok_bottom_comments
            tiktok['shares'] = tiktok_bottom_likes
            tiktoks.append(tiktok)

        except:
            # we don't care at this stage...
            pass

    # scroll to the bottom
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)

    
