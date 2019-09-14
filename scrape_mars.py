#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from splinter import Browser
from bs4 import BeautifulSoup
import requests
import os
import pymongo
from pprint import pprint
import time

debug_mode = False


def scrape():
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)

    # URL of page to be scraped
    url = 'https://mars.nasa.gov/news/'

    browser.visit(url)

    # it takes a second for javascript to run and generate html of page
    time.sleep(1)

    html = browser.html

    # Create BeautifulSoup object
    soup = BeautifulSoup(html, 'html.parser')

    news_title = soup.find("div", class_="list_text").a.text

    if debug_mode:
        print(news_title)

    news_p = soup.find("div", class_="article_teaser_body").text

    if debug_mode:
        print(news_p)

    # URL of page to be scraped
    base_url = 'https://www.jpl.nasa.gov'
    soup_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'

    browser.visit(soup_url)

    time.sleep(1)

    html = browser.html

    soup = BeautifulSoup(html, 'html.parser')

    img_anchor = soup.find("a", class_="button fancybox")
    featured_img_url = base_url + img_anchor.get("data-fancybox-href")

    if debug_mode:
        print(featured_img_url)

    # URL of page to be scraped
    base_url = 'https://twitter.com/marswxreport'
    soup_url = 'https://twitter.com/marswxreport?lang=en'

    browser.visit(soup_url)

    time.sleep(1)

    html = browser.html

    soup = BeautifulSoup(html, 'html.parser')

    tweet_p = soup.find_all("p", class_="tweet-text")

    for tweet in tweet_p:
        if tweet.text.startswith("InSight"):
            mars_weather = tweet.text
            break

    if debug_mode:
        print(mars_weather)

    facts_url = "https://space-facts.com/mars/"

    tables = pd.read_html(facts_url)

    facts_table = tables[1]
    facts_table = facts_table.rename(columns={0: "Description", 1: "Value"})
    facts_table = facts_table.set_index("Description")

    if debug_mode:
        print(facts_table)

    facts_html = facts_table.to_html().replace('\n', '')

    if debug_mode:
        print(facts_html)

    # The site for Mars hemisphere images referenced in homework returns error 404.
    # I found a page at "The Planetary Society" that includes Mars hemisphere images
    # I am using that.  Hopefully it does not go 404 soon!

    # URL of page to be scraped
    url = 'http://www.planetary.org/blogs/guest-blogs/bill-dunford/20140203-the-faces-of-mars.html'

    browser.visit(url)

    # it takes a second for javascript to run and generate html of page
    time.sleep(1)

    html = browser.html

    soup = BeautifulSoup(html, 'html.parser')

    # All the hemisphere images at this site have a class of "img840"
    images_list = soup.find_all("img", class_="img840")

    hemisphere_image_urls = []

    for img in images_list:
        img_title = img.get("alt")
        img_url = img.get("src")
        img_dict = {"title": img_title, "img_url": img_url}
        hemisphere_image_urls.append(img_dict)

    if debug_mode:
        print(hemisphere_image_urls)

    mars_dict = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_img_url": featured_img_url,
        "mars_weather": mars_weather,
        "facts_html": facts_html,
        "hemisphere_image_urls": hemisphere_image_urls
    }

    if debug_mode:
        pprint(mars_dict)

    browser.quit()

    return mars_dict
