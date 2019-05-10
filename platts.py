from selenium import webdriver
from utils import shorten_url
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

def process_platts_output(res_df, url_shorten_api, url_shorten_workspace):
    """
    Generate wechat message to send based on result dataframe

    :param res_df: result dataframe
    :type res_df: pandas.DataFrame

    :param url_shorten_api: URL Link Shortener API
    :type url_shorten_api: str

    :param url_shorten_workspace: URL Link Shortener workspace ID
    :type url_shorten_workspace: str

    :return: processed string
    """

    res_df['shorten_url'] = res_df['url'].apply(lambda x: shorten_url(x, url_shorten_api, url_shorten_workspace))
    res_df = res_df.loc[-res_df['shorten_url'].str.startswith('https')].reset_index(drop=True)
    res_df['shorten_url'] = 'https://' + res_df['shorten_url']

    msg = ''

    for i in res_df.iterrows():
        news_info = "{}\n{}\n-------\n".format(i[1]['title'], i[1]['shorten_url'])
        msg += news_info

    return msg


