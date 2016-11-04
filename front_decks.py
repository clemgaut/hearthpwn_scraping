#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import json
import datetime

PHANTOM_JS_PATH = r"./phantomjs-2.1.1-windows/bin/phantomjs.exe"


driver = webdriver.PhantomJS(PHANTOM_JS_PATH)

driver.get("http://www.hearthpwn.com")

waiter = WebDriverWait(driver, 10)
element = waiter.until(EC.presence_of_element_located((By.XPATH,'//ul[@class="decks"]/li')))

html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")

soup = BeautifulSoup(html)
top_decks = []

for deck in soup.find_all(class_=re.compile("type_ranked-deck")):
    deck_descr = {}

    for c in deck.get("class"):
        if "class" in c:
            deck_descr["class"] = c.split("_")[1]

    deck_descr['link'] = deck.a.get('href')
    deck_descr['rating'] = deck.find("div", class_="rating tip").text
    deck_descr['last_edit'] = deck.find("abbr", class_="tip").text

    engagements = deck.find("ul", class_="deck-engagement")
    for eng in engagements.find_all("li"):
        if "Views" in eng.text:
            deck_descr['views'] = eng.text.split()[0]
        if "Comments" in eng.text:
            deck_descr['comments'] = eng.text.split()[0]
    top_decks.append(deck_descr)

driver.quit()

with open("hearthpwn_top_deck_" + str(datetime.datetime.now().timestamp()) + ".json", "w") as f:
    json.dump(top_decks, f)
