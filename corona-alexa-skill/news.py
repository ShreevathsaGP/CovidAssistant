from passwords import api_key
from newsapi import NewsApiClient
from datetime import datetime, timedelta, date
import country_converter as coco
from passwords import api_key

class Scraper:
    def __init__(self):
        self.time_start = str(date.today() - timedelta(days=7))
        self.newsapi = NewsApiClient(api_key=api_key) # api_key is in passwords.py file
    
    def get_global_news(self):
        data = self.newsapi.get_top_headlines(q='covid-19', language='en')
        articles = data['articles']
        
        global_news = {}
        
        for article in articles:
            global_news.update({article['author'] : article['description']})

        return global_news

    def get_country_news(self, country):
        data = self.newsapi.get_top_headlines(q='covid-19', country=country)
        articles = data['articles']

        country_news = {}

        for article in articles:
            country_news.update({article['author'] : article['description']})

        return country_news