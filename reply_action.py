# -*- coding: utf-8 -*-

from news_bus_weather import *
from jobstreet import *
from utils import *
from platts import *
import os
import time


def reply_weather(weather_api, city='Singapore'):
    """
    generate weather meassgae

    :param city: city to check
    :type city: str

    :param weather_api: Open Weather API key
    :type weather_api: str

    :return: text message
    """
    weather_df = get_weather(city, weather_api)
    message = """今天的天气是这样的:\n湿度: {}\n温度: {}摄氏度 (最低. {}, 最高. {})\n预计天气为: {}""".format(
        weather_df['humidity'], weather_df['temp'], weather_df['temp_min'], weather_df['temp_max'],
        weather_df['weather'])
    return message


def reply_news(msg, news_api, news_latest, news_sources, news_cnt, url_api, url_workspace, user):
    """
    generate news pdf and reply to the user

    :param msg: wxpy meassage object
    :type msg: wxpy meassage object

    :param news_api: News API
    :type news_api: str

    :param news_latest: latest days news to extract
    :type news_latest: int

    :param news_sources: news sources
    :type news_sources: list

    :param news_cnt: number of news to extract
    :type news_cnt: int

    :param url_api: url shorten api
    :type url_api: str

    :param url_workspace: url shorten workspace id
    :type url_workspace: str

    :param user: WeChat user to reply to
    :type user: wxpy user

    :return: None
    """
    if msg.text.startswith('新闻 '):
        topics = msg.text[3:].split(', ')
        news_df = get_news(news_api, topics, news_latest, news_sources, news_cnt)
    else:
        news_df = get_news(news_api, [], news_latest, news_sources, news_cnt, kind='headline')

    # create news pdf
    news_file = '{}_{}'.format(msg.text, user.name)
    # news_pdf = news_file+'.pdf'
    # create_pdf(news_df, news_file)
    user.send("新闻正在生成中...稍等！")

    # create news message
    news_df.columns = [i.lower() for i in news_df.columns]
    message = process_news_output(news_df, url_api, url_workspace)

    # send message to user
    if message != '':
        user.send("相关新闻如下：\n" + message)
    else:
        user.send("没有相关新闻，请尝试其他关键词，如'Finance'")

    # # send pdf file
    # user.send_file(news_pdf)
    # user.send("更多新闻请参阅此文档")
    # os.remove(news_pdf)

    return


def reply_bus(msg, lta_api):
    """
    reply next 3 buses waiting time

    :param msg: wxpy meassage object
    :type msg: wxpy meassage object

    :param lta_api: LTA DataMall API Key
    :type lta_api: str

    :return: text message
    """
    # short cut for qiaoling and NCS
    if msg.text == '坐巴士':
        msg = ['63291', '53.45.53m']
    elif msg.text == '巴士ncs':
        msg = ['55039']
    else:
        # extract bus stop number and potentially, bus lists
        msg = msg.text.lower()[3:].split(" ")

    busstop = msg[0]
    if len(msg) == 1:
        bus_list = None
    else:
        bus_list = msg[1].split('.')

    bus_df = get_next_bus(lta_api, busstop, bus_list)

    if len(bus_df) == 0:
        return "目前好像已经没有巴士了呢...或者出问题了！"
    else:
        message = ""
        for i in bus_df[['bus_number', 'first_interval', 'second_interval', 'third_interval']].iterrows():
            bus_record = list(i[1])
            bus_record = [bus_record[0]] + [86400 - i if i > 80000 else i for i in bus_record[1:]]
            message += "巴士: {}\n下一班 {} 分钟\n下下一班 {} 分钟\n下下下一班 {} 分钟\n========\n". \
                format(bus_record[0], round(bus_record[1] / 60, 1), round(bus_record[2] / 60, 1),
                       round(bus_record[3] / 60, 1))
        return message


def reply_jobs(msg, driver_path, js_url, js_username, js_password, js_pages, sender_email, sender_password, user):
    """
    generate jobs pdf and send to user email

    :param msg: wxpy meassage object
    :type msg: wxpy meassage object

    :param driver_path: chrome driver path
    :type driver_path: str

    :param js_url: JobStreet login page url
    :type js_url: str

    :param js_username: JobStreet username
    :type js_username: str

    :param js_password: JobStreet password
    :type js_password: str

    :param js_pages: number of pages of job postings to extract
    :type js_pages: int

    :param sender_email: sender's email
    :type sender_email: str

    :param sender_password: sender's password
    :type sender_password: str

    :param user: WeChat user to reply to
    :type user: wxpy user

    :return: None
    """
    user.send('生成工作信息中，需要等待一段时间，请稍候...')

    email = msg.text.split('^')[-1]
    keywords = msg.text.split('^')[0][3:].strip().split(', ')
    driver = initialise_driver(js_url, driver_path)
    driver = login(driver, js_username, js_password)

    res_l = []
    for kwd in keywords:
        driver = search_keyword(driver, kwd)
        for _ in range(js_pages):
            time.sleep(2)
            driver, page_info = extract_data(driver)
            res_l.append(page_info)
            driver = next_page(driver)
    res_df = pd.concat(res_l)
    driver, app_df = extract_requirements(driver, res_df['url'])

    driver.quit()

    res_df = res_df.merge(app_df, on='url', how='left')
    res_df = process_jobs_output(res_df)
    file_name = '{}_{}'.format(msg.text, user.name)
    create_pdf(res_df, file_name)


    body = 'To be updated'

    send_email(sender_email, sender_password, email, file_name, body, file_name+'.pdf')
    user.send('工作信息已经被发送至{}, 请查收'.format(email))
    os.remove(file_name+'.pdf')
    return


def reply_platts(driver_path, platts_url, platts_pages, url_api, url_workspace, user):
    """
    generate platts meassgae

    :param driver_path: webdriver path
    :type driver_path: str

    :param platts_url: platts url
    :type platts_url: str

    :param platts_pages: pages to load
    :type platts_pages: int

    :param url_api: url shorten api
    :type url_api: str

    :param url_workspace: url shorten workspace id
    :type url_workspace: str

    :param user: WeChat user to reply to
    :type user: wxpy user

    :return: message string
    """

    user.send("生成Platts 新闻中...请稍候")
    driver = initialise_platts_driver(platts_url, driver_path)
    driver = click_options(driver)
    res = []

    for _ in range(platts_pages):
        driver = load_more_page(driver)
        time.sleep(2)
        driver = scroll_down(driver)
        time.sleep(2)
        driver, res_df = extract_news(driver)

        res.append(res_df)
    driver.quit()

    msg = process_news_output(res_df, url_api, url_workspace)

    user.send("最新Platts 新闻如下：")
    return msg

def reply_test():
    """
    return instruction for test

    :return: instruction text
    """

    message = '可使用的口令如下：\n\n' \
              '1. 天气 -- 返回天气预测\n' \
              '2. 头条 -- 返回今日CNN，BBC新闻头条\n' \
              '3. platts -- 返回platts 新闻\n\n' \
              '4. 新闻 topic1, topic2 .. , topicX -- 根据所选主题，返回新闻\n' \
              '例：新闻 nba, finance\n\n' \
              '5. 巴士 bus stop number，[bus1.bus2. .. .busX] -- 根据所选巴士站号码及巴士号码，返回接下来三班巴士抵达时间\n' \
              '例：巴士 63291, 53.45.53m\n\n' \
              '6. 工作 job1, job2 .. , jobX ^email@email.com -- 爬取相关工作并发送结果至指定邮箱\n'\
              '例： 工作 data scientist, data analyst ^sunwrn@gmail.com\n'

    return message