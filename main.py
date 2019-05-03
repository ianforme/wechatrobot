import config
from process import get_weather, get_news, get_next_bus

city = config.city
weather_api = config.weather_api
news_api = config.news_api
news_topics = config.topics
news_latest = config.latest
news_sources = config.sources
news_cnt = config.article_cnt

get_weather(city, weather_api)

get_news(news_api, news_topics, news_latest, news_sources, news_cnt)