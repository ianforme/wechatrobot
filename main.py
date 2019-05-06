import config
from process import get_weather, get_news, get_next_bus, create_pdf
from wxpy import *
import time
import os

city = config.city
lta_api = config.lta_api
weather_api = config.weather_api
news_api = config.news_api
news_topics = config.topics
news_latest = config.latest
news_sources = config.sources
news_cnt = config.article_cnt
wechat_user =config.wechat_user

bot = Bot(cache_path=True)

# reply to specific friend or all
if wechat_user != "":
    user = bot.search(wechat_user)[0]
else:
    user = None

@bot.register(user)
def auto_reply(msg):
    print(msg)
    # check whehter the user ask for weather
    if msg.text == '天气':
        weather_df = get_weather(city, weather_api)
        message = """宝贝今天的天气是这样的:\n湿度: {}\n温度: {}摄氏度 (最低. {}, 最高. {})\n目前状况是: {}""".format(
            weather_df['humidity'], weather_df['temp'], weather_df['temp_min'], weather_df['temp_max'], weather_df['weather'])
        return message

    # check whether the user is asking for news by topic
    if msg.text.startswith('新闻 ') or msg.text == '头条':
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
            user.send("好像出问题了...联系孙孙！")
        return

    # check wther the user is asking for next bus arrival time at any bus stop
    if msg.text.startswith("巴士 ") or msg.text == '坐巴士' or msg.text == '巴士ncs':

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
            return "目前好像已经没有巴士了呢...或者出问题了，联系孙孙！"
        else:
            message = ""
            for i in bus_df[['bus_number', 'first_interval', 'second_interval', 'third_interval']].iterrows():
                bus_record = list(i[1])
                bus_record = [bus_record[0]] + [86400 - i if i > 80000 else i for i in bus_record[1:]]
                message += "巴士: {}\n下一班 {} 分钟\n下下一班 {} 分钟\n下下下一班 {} 分钟\n========\n".\
                    format(bus_record[0], round(bus_record[1]/60, 1), round(bus_record[2]/60, 1), round(bus_record[3]/60, 1))
            return message

