import requests, json
import pandas as pd
from newsapi import NewsApiClient

def get_weather(city_name, weather_api):
    """
    given a city name and api key for Open Weather Map, return local weather conditions

    :param city_name: name of the city
    :type city_name: str

    :param weather_api: Open Weather Map API
    :type weather_api: str

    :return: results dictionary
    """

    response = requests.get(
        "https://community-open-weather-map.p.rapidapi.com/weather?mode=json&q={}".format(city_name),
        headers={
            "X-RapidAPI-Host": "community-open-weather-map.p.rapidapi.com",
            "X-RapidAPI-Key": weather_api
        })

    content = json.loads(response.content.decode('utf8').replace("'", '"'))

    res_dict = dict()
    res_dict['humidity'] = content['main']['humidity']
    res_dict['temp'] = round((content['main']['temp'] - 273.15), 1)
    res_dict['temp_max'] = round((content['main']['temp_max'] - 273.15), 1)
    res_dict['temp_min'] = round((content['main']['temp_min'] - 273.15), 1)
    res_dict['weather'] = content['weather'][0]['main']

    return res_dict


def get_next_bus(lta_api, busstop, bus_list=None):
    """
    given a bus stop code return estimated arrival time for the next 3 buses of each bus in the bus list

    :param lta_api: LTA DataMall API Key
    :type lta_api: str

    :param busstop: bus stop code
    :type busstop: str

    :param bus_list: list of bus to watch, if None, all will be taken
    :type bus_list: list

    :return: results dataframe
    """

    response = requests.get(
        "http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2?BusStopCode={}".format(busstop),
        headers={'AccountKey': lta_api,
                 'accept': 'application/json'
                 })
    content = json.loads(response.content.decode('utf8').replace("'", '"'))

    if len(content['Services']) == 0:
        return "已经没有巴士了..."

    buses_info = []
    for service in content['Services']:
        # Extract bus number
        bus_number = service['ServiceNo']
        # Extract estimated arrival time for the next bus
        try:
            first_arrival = pd.to_datetime(service['NextBus']['EstimatedArrival'], format='%Y-%m-%dT%H:%M:%S+08:00')
        except:
            first_arrival = None
        # Extract estimated arrival time for the second next bus
        try:
            second_arrival = pd.to_datetime(service['NextBus2']['EstimatedArrival'], format='%Y-%m-%dT%H:%M:%S+08:00')
        except:
            second_arrival = None
        # Extract estimated arrival time for the third next bus
        try:
            third_arrival = pd.to_datetime(service['NextBus3']['EstimatedArrival'], format='%Y-%m-%dT%H:%M:%S+08:00')
        except:
            third_arrival = None
        # Aggregation
        buses_info.append([bus_number, first_arrival, second_arrival, third_arrival])

    res_df = pd.DataFrame(buses_info, columns=['bus_number', 'first_arrival', 'second_arrival', 'third_arrival'])

    # only select target buses if its given
    if bus_list:
        res_df = res_df.loc[res_df['bus_number'].str.lower().isin(bus_list)]

    res_df['current_time'] = pd.Timestamp.now()
    res_df['first_interval'] = (res_df['first_arrival'] - res_df['current_time']).dt.seconds
    res_df['second_interval'] = (res_df['second_arrival'] - res_df['current_time']).dt.seconds
    res_df['third_interval'] = (res_df['third_arrival'] - res_df['current_time']).dt.seconds

    return res_df

def get_news(news_api, topics, latest, sources, article_cnt, kind='news'):
    """
    given a topic, extract latest trending news / headlines from sources

    :param news_api: newsapi
    :type news_api: str

    :param topics: list of topic to search for
    :type topics: list

    :param latest: maxmium number of days to trace back
    :type latest: int

    :param sources: news sources
    :type sources: list

    :param article_cnt: number of articles to return
    :type article_cnt: int

    :param kind: headline or news, if headline is chosen, topic is ignored
    :type kind: str

    :return: results dataframe
    """

    # init
    client = NewsApiClient(api_key=news_api)

    # create filters
    earliest_date = (pd.Timestamp.now() - pd.Timedelta('{}Day'.format(latest))).strftime(format='%Y-%m-%d')
    sources = ",".join(sources)

    # /v2/everythin
    articles_info = []
    if kind == 'news':
        # to extract historical news based on topic
        for topic in topics:
            articles = client.get_everything(q=topic,
                                             sources=sources,
                                             from_param=earliest_date,
                                             language='en',
                                             sort_by='publishedAt',
                                             page_size=article_cnt)['articles']

            # extract description abt the article
            for article in articles:
                title = article['title']
                author = article['author']
                source = article['source']['name']
                published_at = article['publishedAt']
                description = article['description']
                url = article['url']

                articles_info.append([title, description, author, source, topic, published_at, url])

        res_df = pd.DataFrame(articles_info,
                              columns=['Title', 'Description', 'Author', 'Source', 'Topic', 'Publish Date', 'URL'])

    else:
        # to extract headlines
        articles = client.get_top_headlines(sources=sources,
                                            language='en',
                                            page_size=article_cnt)['articles']

        for article in articles:
            title = article['title']
            author = article['author']
            source = article['source']['name']
            published_at = article['publishedAt']
            description = article['description']
            url = article['url']

            articles_info.append([title, description, author, source, published_at, url])

        res_df = pd.DataFrame(articles_info,
                              columns=['Title', 'Description', 'Author', 'Source', 'Publish Date', 'URL'])

    return res_df
