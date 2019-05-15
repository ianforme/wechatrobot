# -*- coding: utf-8 -*-

import config
from reply_action import *
from wxpy import *

# api keys
lta_api = config.lta_api
weather_api = config.weather_api
news_api = config.news_api
url_api = config.url_api
url_workspace = config.url_workspace

# news
news_latest = config.news_latest
news_sources = config.news_sources
news_cnt = config.news_article_cnt

# config for jobstreet
driver_path = config.driver_path
js_url = config.js_url
js_username = config.js_username
js_password = config.js_password
js_pages = config.js_pages
js_email = config.js_email
js_email_password = config.js_email_password

# config for platts
platts_url = config.platts_url
platts_pages = config.platts_pages

# wechat user
wechat_user =config.wechat_user

# login the bot
bot = Bot(cache_path=True)

# define target user to reply to
user = bot.search(wechat_user)[0]

@bot.register([user, bot.self], except_self=False)
def auto_reply(msg):
    print(msg)
    # check whehter the user ask for weather
    if msg.text == '天气':
        message = reply_weather(weather_api)
        return message

    # check whether the user is asking for news by topic
    if msg.text.startswith('新闻 ') or msg.text == '头条':
        reply_news(msg, news_api, news_latest, news_sources, news_cnt, url_api, url_workspace, msg.sender)
        return None

    # check whether the user is asking for next bus arrival time at any bus stop
    if msg.text.startswith("巴士 ") or msg.text == '坐巴士' or msg.text == '巴士ncs':
        message = reply_bus(msg, lta_api)
        return message

    # check whether the use is ask for jobs
    if msg.text.startswith("工作 "):
        reply_jobs(msg, driver_path, js_url, js_username, js_password, js_pages, js_email, js_email_password, msg.sender)
        return None

    # check whether the user is asking for platts headlines
    if msg.text.lower() == 'platts':
        message = reply_platts(driver_path, platts_url, platts_pages, url_api, url_workspace, msg.sender)
        return message

    # return test guide
    if msg.text == '测试指南':
        message = reply_test()
        return message

