# -*- coding: utf-8 -*-

from selenium import webdriver
import pandas as pd

def initialise_platts_driver(url, path):
    """
    Initialise the chrome driver

    :param url: platts url
    :type url: str

    :param path: driver path
    :type path: str

    :return: webdriver
    """

    # Initialise the driver
    chrome_options = webdriver.ChromeOptions()

    # This setting prevent website from sending notifications
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(path, chrome_options=chrome_options)

    # Target URL
    driver.get(url)

    return driver

def click_options(driver):
    """
    choose topics for platts news based on user input

    :param driver: webdriver
    :type driver: webdriver

    :return: webdriver
    """

    driver.find_element_by_xpath('//label[@for="commodity2"]').click()
    driver.find_element_by_xpath('//label[@for="commodity7"]').click()
    driver.find_element_by_xpath('//label[@for="commodity8"]').click()

    return driver

def extract_news(driver):
    """
    extract news:
    - title
    - topic
    - date
    - url

    :param driver: webdriver
    :type driver: webdriver

    :return: driver, pandas Dataframe
    """

    news_topic = [i.text for i in driver.find_elements_by_xpath("//div[@class='newsId']/a[@data-gtm-category='News Feed']/div/ul/li[@class='meta-data__type']")]
    news_date = [i.text for i in driver.find_elements_by_xpath("//div[@class='newsId']/a[@data-gtm-category='News Feed']/div/ul/li[@class='meta-data__date']")]
    news_title = [i.text for i in driver.find_elements_by_xpath("//div[@class='newsId']/a/div/h2")]
    news_url = [i.get_attribute('href') for i in driver.find_elements_by_xpath("//div[@class='newsId']/a")]

    res_df = pd.DataFrame({
        'title': news_title,
        'topic': news_topic,
        'date': news_date,
        'url': news_url
    })

    return driver, res_df

def load_more_page(driver):
    """
    Load more news by clicking Load More

    :param driver: webdriver
    :type driver: webdriver

    :return: webdriver
    """

    driver.find_element_by_id("loadMoreNews").click()

    return driver

def scroll_down(driver):
    """
    This function will simulate the scroll down of the webpage

    :param driver: webdriver
    :type driver: webdriver

    :return: webdriver
    """

    # Selenium supports execute JavaScript commands in current window / frame
    # get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    # scroll to the end of the page
    driver.execute_script("window.scrollTo(0, {});".format(last_height))

    return driver



