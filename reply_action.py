from news_bus_weather import *
from jobstreet import *
import os
import time

def reply_weather(city, weather_api):
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

def reply_news(msg, news_api, news_latest, news_sources, news_cnt, user):
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

    :param user: WeChat user to reply to
    :type user: wxpy user

    :return: None
    """
    if msg.text.startswith('新闻 '):
        topics = msg.text[3:].split(', ')
        news_df = get_news(news_api, topics, news_latest, news_sources, news_cnt)
    else:
        news_df = get_news(news_api, [], news_latest, news_sources, news_cnt, kind='headline')

    # create news.pdf
    create_pdf(news_df, 'news')
    user.send("新闻正在生成中...稍等！")

    flag = 0
    # wait for 10 seconds before the pdf is generated
    for _ in range(10):
        # search for the pdf every 1 second
        if os.path.isfile('news.pdf'):
            user.send("这是你要的新闻~")
            user.send_file('news.pdf')
            os.remove('news.pdf')
            flag = 1
            break
        time.sleep(1)
    if flag == 0:
        user.send("好像出问题了...！")
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

def reply_jobs(msg, driver_path, js_url, js_username, js_password, js_pages, user):
    """
    generate jobs pdf and send to user

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
    :param user: int

    :return: None
    """
    user.send('生成工作信息中，需要等待一段时间，请稍候...')

    keywords = msg.text[3:].split(', ')
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

    res_df = res_df.merge(app_df, on='url', how = 'left')
    res_df = process_output(res_df)
    create_pdf(res_df, 'jobs')

    flag = 0
    for _ in range(10):
        # search for the pdf every 1 second
        if os.path.isfile('jobs.pdf'):
            user.send("工作信息生成完毕！")
            user.send_file('jobs.pdf')
            os.remove('jobs.pdf')
            flag = 1
            break
        time.sleep(1)
    if flag == 0:
        user.send("好像出问题了...！")




