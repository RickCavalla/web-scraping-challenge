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

    # Mars News
    url = 'https://mars.nasa.gov/news/'

    browser.visit(url)

    # it takes a second for javascript to run and generate html of page
    time.sleep(1)

    html = browser.html

    # Create BeautifulSoup object
    soup = BeautifulSoup(html, 'html.parser')

    # grab text of first article anchor in list
    news_title = soup.find("div", class_="list_text").a.text

    if debug_mode:
        print(news_title)

    # grab text of first article teaser in list
    news_p = soup.find("div", class_="article_teaser_body").text

    if debug_mode:
        print(news_p)

    # Jet Propulsion Laboratory images
    base_url = 'https://www.jpl.nasa.gov'
    soup_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'

    browser.visit(soup_url)

    time.sleep(1)

    html = browser.html

    soup = BeautifulSoup(html, 'html.parser')

    # a "fancybox" button links to full size image
    # get href link of that button
    img_anchor = soup.find("a", class_="button fancybox")
    featured_img_url = base_url + img_anchor.get("data-fancybox-href")

    if debug_mode:
        print(featured_img_url)

    # Mars weather Twitter
    base_url = 'https://twitter.com/marswxreport'
    soup_url = 'https://twitter.com/marswxreport?lang=en'

    browser.visit(soup_url)

    time.sleep(1)

    html = browser.html

    soup = BeautifulSoup(html, 'html.parser')

    # Not all tweets are weather
    # but weather tweets seems to start with "InSight"
    # so find_all tweet texts and iterate until we find most recent tweet
    # that starts with "InSight"
    tweet_p = soup.find_all("p", class_="tweet-text")

    for tweet in tweet_p:
        if tweet.text.startswith("InSight"):
            mars_weather = tweet.text
            break

    if debug_mode:
        print(mars_weather)

    # Mars facts
    facts_url = "https://space-facts.com/mars/"

    # read html tables
    tables = pd.read_html(facts_url)

    # second table is facts
    facts_table = tables[1]

    # rename default unnamed columns
    facts_table = facts_table.rename(columns={0: "Description", 1: "Value"})

    # drop default index and set it to first data column
    facts_table = facts_table.set_index("Description")

    if debug_mode:
        print(facts_table)

    # make a new html table, but drop the newline characters
    facts_html = facts_table.to_html().replace('\n', '')

    if debug_mode:
        print(facts_html)

    # Hemisphere images
    url_hemi_base = "https://astrogeology.usgs.gov"
    url = url_hemi_base + "/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"

    browser.visit(url)

    # it takes a second for javascript to run and generate html of page
    time.sleep(1)

    html = browser.html

    soup = BeautifulSoup(html, 'html.parser')

    # All hemisphere links are in divs classed "description"
    links_list = soup.find_all("div", class_="description")
    
    hemisphere_image_urls = []

    # loop through list of hemisphere links
    for link in links_list:
        # image title is text of anchor link
        img_title = link.a.text
    
        # link to this hemisphere page
        link_url = url_hemi_base + link.a.get("href")
    
        # visit this hemisphere
        browser.visit(link_url)

        # it takes a second for javascript to run and generate html of page
        time.sleep(1)

        link_html = browser.html
    
        soup_link = BeautifulSoup(link_html, 'html.parser')
    
        # get the src of wide-image class for full size hemisphere image
        img_url = soup_link.find("img", class_="wide-image").get("src")
        img_url = url_hemi_base + img_url
    
        # put title and url in a dictionary
        img_dict = {"title": img_title, "img_url": img_url}
    
        # push dictionary into list of all hemispheres
        hemisphere_image_urls.append(img_dict)
    
    if debug_mode:
        print(hemisphere_image_urls)

    # create a big dictionary with all mars data
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
