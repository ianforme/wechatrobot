# WeChatBot
WeChatBot is a customized chat bot built on Python that acts as a WeChat personal assistant for Qiaoling


## Introduction
As for now, she is able to 

- ask for weather
- ask for news by topic from BBC and CNN
- ask for bus arrival time
- ask for news headlines
- ask for jobs

In the future editions, these features will be added in

- ask for platts news(www.spglobal.com/platts/en/market-insights/latest-news#)
- ask for discount and promo

## Dependencies

- Python 3.6
- wxpy
- reportlab
- selenium
- [Open Weather Map](https://rapidapi.com/community/api/open-weather-map)
- [News API](https://newsapi.org/)
- [LTA DataMall](https://www.mytransport.sg/content/mytransport/home/dataMall.html)
- [URL Shortener API](https://developers.rebrandly.com/docs/api-custom-url-shortener)
- And of course you will need to have a WeChat account to play with

## Installation & Setup
- Clone the repo (and give it a star if you like it~)
- Apply API keys from LTA DataMall, Open Weather Map, News API, URL shortener API
- Sign up a jobstreet.com account
- Key in your credentials to config file
- Configure the user you want to respond to in the config file
- Run main.py script
- Scan the QR Code with your robot WeChat account
- Usage of the other parameters in config.py are:
    - city: weather of this city
    - topics: not in use for now, future prove
    - latest: controls latency of news on specific topic to be extracted, unit is day
    - sources: news sources, refers News API for more sources available
    - article_cnt: number of articles to return for each news topic

## Example
Currently the robot is able to do the following:
- returning weather condition when asked by '天气'
- returning headline news from CNN and BBC when asked by '头条'
- returning news about specific topics from CNN and BBC when asked by '新闻 topic1, topic2, .. ,topicX'
- returning bus arrival time at speicfic bus stop when asked by '巴士 bus_stop_number, bus1.bus2.bus3 .. .busX'
- returning 53, 45 and 53M bus arrival time at 63291 (for QL) when asked by '坐巴士'
- returning bus arrival time at 55039 (at back door of NCS)  when asked by '巴士ncs'
- returning jobs from jobstreet.com when asked by '工作 job1, job2, .. , jobX'
 
## License
The software is under MIT License

Powered by NewsAPI.org
 
