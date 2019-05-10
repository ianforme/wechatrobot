from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import numpy as np
import time

def initialise_driver(url, path):
    """
    Initialise the chrome driver

    :param url: jobstreet url
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


def login(driver, username, password):
    """
    Simulate login account

    :param driver: webdriver
    :type driver: webdriver

    :param username: jobstreet username
    :type username: str

    :param password: jobstreet password
    :type password: str

    :return: driver: webdriver
    """
    # Simulate login
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "login_id"))
    ).send_keys(username)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "password"))
    ).send_keys(password)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "btn_login"))
    ).click()

    return driver


def search_keyword(driver, keyword):
    """
    Search by keywords

    :param driver: webdriver
    :type driver: webdriver

    :param keyword: job title / keywords
    :type keyword: str

    :return: webdriver
    """
    first_keyword = keyword
    driver.find_element_by_id("search_box_keyword").clear()
    driver.find_element_by_id("search_box_keyword").send_keys(first_keyword)
    driver.find_element_by_id("header_searchbox_btn").click()

    return driver


def extract_data(driver):
    """
    For each job posted, extract:
        - job title
        - company
        - location
        - description
        - post dates
        - url

    :param driver: webdriver
    :type driver: webdriver

    :return: list of webdriver and data frame
    """
    # Extract all the displayed components + and all the relevant panels on the webpage
    panels = driver.find_elements_by_xpath(
        "//div[not(contains(@style,'display:none'))]/div[@id[starts-with(.,'job_ad_')]]")

    # Create result dictionary
    res_dict = {
        'job_title': [],
        'company': [],
        'description': [],
        'recency': [],
        'url': [],
    }

    # for each panel, extract relevant information
    for i, panel in enumerate(panels):

        # For job title and url
        try:
            title = panel.find_element_by_class_name('position-title-link').text
            url = panel.find_element_by_class_name('position-title-link').get_attribute('href')

        except:
            title = None
            url = None

        # For company name
        try:
            company = panel.find_element_by_class_name('company-name').text
        except:
            company = None

        # For description
        try:
            description = panel.find_element_by_id('job_desc_detail_{}'.format(i + 1)).text
        except Exception as e:
            print(e)
            description = None

        # For post dates
        try:
            recency = panel.find_element_by_id('posted_datetime_{}'.format(i + 1)).text
        except:
            recency = None

        # aggregate results
        res_dict['job_title'].append(title)
        res_dict['company'].append(company)
        res_dict['description'].append(description)
        res_dict['recency'].append(recency)
        res_dict['url'].append(url)

    res_df = pd.DataFrame(res_dict)

    return [driver, res_df]

def extract_requirements(driver, url_list):
    """
    Extract job requirements and keywords from a list of posting urls

    :param driver: webdriver
    :type driver: webdriver

    :param url_list: list of job posting urls
    :type url_list: pandas.Series

    :return: job requirements pandas dataframe
    """

    exp_l = []
    edu_l = []
    salary_l = []
    location_l = []

    for url in url_list:
        driver.get(url)
        time.sleep(5)
        # get years of experiences
        try:
            experience = driver.find_element_by_id("years_of_experience").text
        except:
            experience = None

        # get the salary range
        try:
            salary_range = driver.find_element_by_id('salary_range').text
        except:
            salary_range = None

        # get the location
        try:
            location = driver.find_element_by_id('single_work_location').text
        except:
            location = None

        # extract the job description
        jd_txt = driver.find_element_by_id('job_description').text.lower()

        # get education requirement
        education_lvl = ['bachelor', 'master', 'phd', 'doctor', 'diploma']
        education_req = ', '.join([i for i in education_lvl if i in jd_txt])

        if education_req == '':
            education_req = None

        # TODO: Keywords extraction based text analysis and NLP, refine education keywords extraction as well

        exp_l.append(experience)
        edu_l.append(education_req)
        salary_l.append(salary_range)
        location_l.append(location)

    res_df = pd.DataFrame({
        'url' : url_list,
        'experience' : exp_l,
        'education' : edu_l,
        'salary': salary_l,
        'location': location_l
    })

    return driver, res_df

def next_page(driver):
    """
    Navigate to next page

    :param driver: webdriver
    :type driver: webdriver

    :return: webdriver
    """

    driver.find_element_by_id("page_next").click()

    return driver


def process_jobs_output(final_df):
    """
    preprocess the dataframe before creating pdf

    :param final_df: final dataframe
    :type final_df: pandas.DataFrame

    :return: processed dataframe
    """

    output_df = final_df.copy()
    output_df['job_title'] = np.where(output_df['job_title'].str.len() > 30, output_df['job_title'].str[:30] + "...",
                                      output_df['job_title'].str[:30])

    output_df['description'] = np.where(output_df['description'].str.len() > 100, output_df['description'].str[:100] + "...",
                                      output_df['description'].str[:100])

    # add url to title
    output_df['job_title_url'] = '<link href="' + output_df['url'] + '">'+output_df['job_title'] + '</link>'

    # reorder the table
    output_df = output_df[['job_title_url', 'company', 'experience', 'education', 'salary', 'description', 'location']]

    # rename the columns
    output_df.columns = ['Job Title', 'Company', 'Experience', 'Education', 'Salary', 'Description', 'Location']

    return output_df