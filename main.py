import config
from reply_action import *
from wxpy import *

# config for bus, news and weather
city = config.city
lta_api = config.lta_api
weather_api = config.weather_api
news_api = config.news_api
news_latest = config.latest
news_sources = config.sources
news_cnt = config.article_cnt
wechat_user =config.wechat_user

# config for jobstreet
driver_path = config.driver_path
js_url = config.url
js_username = config.username
js_password = config.password
js_pages = config.pages

# login the bot
bot = Bot(cache_path=True)

# define target user to reply to
user = bot.search(wechat_user)[0]

# for testing, remove after testing
user = bot.self

@bot.register(user, except_self=False)
def auto_reply(msg):
    print(msg)
    # check whehter the user ask for weather
    if msg.text == '天气':
        message = reply_weather(city, weather_api)
        return message

    # check whether the user is asking for news by topic
    if msg.text.startswith('新闻 ') or msg.text == '头条':
        reply_news(msg, news_api, news_latest, news_sources, news_cnt, user)
        return None

    # check whether the user is asking for next bus arrival time at any bus stop
    if msg.text.startswith("巴士 ") or msg.text == '坐巴士' or msg.text == '巴士ncs':
        message = reply_bus(msg, lta_api)
        return message

    # check whether the use is ask for jobs
    if msg.text.startswith("工作 "):
        reply_jobs(msg, driver_path, js_url, js_username, js_password, js_pages, user)
        return None