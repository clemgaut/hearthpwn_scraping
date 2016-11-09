#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import sys, os
import argparse
import jsonpickle
import datetime
import sqlite3
from objects import FrontDeckInfo

FRONT_DECKS_TABLE_NAME = "front_decks"
DECKS_TABLE_NAME = "decks"


def extract_front_decks(phantom_js_path=r"./phantomjs-2.1.1-windows/bin/phantomjs.exe"):
    driver = webdriver.PhantomJS(phantom_js_path)

    driver.get("http://www.hearthpwn.com")

    waiter = WebDriverWait(driver, 10)
    waiter.until(EC.presence_of_element_located((By.XPATH,'//ul[@class="decks"]/li')))

    html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")

    soup = BeautifulSoup(html, "lxml")
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


def save_to_json(top_decks, dir = "", file_prefix="hearthpwn_top_decks_"):
    """
    Save the current decks into a json file named prefix+timestamp.json
    :param top_decks: The decks to save. A list of FrontDeckInfo
    :param file_prefix: The json file prefix
    :return:
    """
    with open(os.path.join(dir, file_prefix) + str(datetime.datetime.now().timestamp()) + ".json", "w") as f:
        f.write(jsonpickle.encode(top_decks))


def save_to_sqlite(top_decks, db_file="hearth_pwn_scrap.db"):
    """
    Saves the front decks to an sqlite table. The table is created if it does not exist.
    :param top_decks: The decks to save. A list of FrontDeckInfo
    :param db_file: The database name
    :return:
    """
    create_sqlite_table(db_file)
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    timestamp = datetime.datetime.now().timestamp()

    for deck in top_decks:
        id_deck = c.execute("SELECT id FROM " + DECKS_TABLE_NAME + " WHERE link='" + deck.link + "'")
        if not id_deck.fetchone():
            c.execute("INSERT INTO " + DECKS_TABLE_NAME + " (link) VALUES ( '" + deck.link + "')")
        c.execute("INSERT INTO " + FRONT_DECKS_TABLE_NAME +
                " (deck_id, hs_class, rating, last_edit, views, comments, timestamp) "
                "values ( (SELECT id FROM " + DECKS_TABLE_NAME + " WHERE link='" + deck.link + "'), ?, ?, ? ,?, ?, ?)",
                (deck.hs_class, deck.rating, deck.last_edit, deck.views, deck.comments, timestamp))
    c.close()
    conn.commit()
    conn.close()


def create_sqlite_table(db_file):
    """
    Create the sqlite tables for decks and front decks description if they do not exist
    :return:
    """
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    # We create the table of hearthpwn decks if it does not exists
    c.execute("CREATE TABLE IF NOT EXISTS " + DECKS_TABLE_NAME +
              " (id INTEGER PRIMARY KEY,link TEXT)")

    c.execute("CREATE TABLE IF NOT EXISTS " + FRONT_DECKS_TABLE_NAME +
              " (id INTEGER PRIMARY KEY,deck_id INTEGER, hs_class TEXT, rating INTEGER,last_edit TEXT, views TEXT, comments INTEGER, timestamp INTEGER,"
              "FOREIGN KEY(deck_id) REFERENCES " + DECKS_TABLE_NAME + "(id))")
    c.close()
    conn.commit()
    conn.close()


if __name__ == "__main__":
    top_decks = []
    parser = argparse.ArgumentParser()
    parser.add_argument("--phantomjsPath", help="Path to the phantomJS exe")
    parser.add_argument("--storagePath", help="Path to the storage file (db file if sqlite and directory if json)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--sqlite", help="Activate storage in sqlite database", action="store_true")
    group.add_argument("--json", help="Activate storage in json format (default option)", action="store_true")
    args = parser.parse_args()

    storage_func = save_to_json
    if args.sqlite:
        storage_func = save_to_sqlite

    if args.phantomjsPath:
        top_decks = extract_front_decks(phantom_js_path=args.phantomjsPath)
    else:
        top_decks = extract_front_decks()
    if args.storagePath:
        storage_func(top_decks, args.storagePath)
    else:
        storage_func(top_decks)