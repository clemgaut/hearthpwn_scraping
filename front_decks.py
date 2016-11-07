#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import json
import jsonpickle
import datetime
import sqlite3
from objects import FrontDeckInfo


def extract_front_decks(phantom_js_path=r"./phantomjs-2.1.1-windows/bin/phantomjs.exe"):
    driver = webdriver.PhantomJS(phantom_js_path)

    driver.get("http://www.hearthpwn.com")

    waiter = WebDriverWait(driver, 10)
    waiter.until(EC.presence_of_element_located((By.XPATH,'//ul[@class="decks"]/li')))

    html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")

    soup = BeautifulSoup(html)
    top_decks = []

    for deck in soup.find_all(class_=re.compile("type_ranked-deck")):
        deck_descr = {}

        for c in deck.get("class"):
            if "class" in c:
                deck_descr["hs_class"] = c.split("_")[1]

        deck_descr['link'] = deck.a.get('href')
        deck_descr['rating'] = deck.find("div", class_="rating tip").text
        deck_descr['last_edit'] = deck.find("abbr", class_="tip").text

        engagements = deck.find("ul", class_="deck-engagement")
        for eng in engagements.find_all("li"):
            if "Views" in eng.text:
                deck_descr['views'] = eng.text.split()[0]
            if "Comments" in eng.text:
                deck_descr['comments'] = eng.text.split()[0]
        top_decks.append(FrontDeckInfo(**deck_descr))
    driver.quit()
    return top_decks


def save_to_json(top_decks, file_prefix="hearthpwn_top_decks_"):
    """
    Save the current decks into a json file named prefix+timestamp.json
    :param top_decks: The decks to save. A list of dict
    :param file_prefix: The json file prefix
    :return:
    """
    with open(file_prefix + str(datetime.datetime.now().timestamp()) + ".json", "w") as f:
        f.write(jsonpickle.encode(top_decks))

if __name__ == "__main__":
    top_decks = extract_front_decks()
    save_to_json(top_decks)