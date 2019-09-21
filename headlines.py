import feedparser
import json
import requests

from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

DEFAULTS = {
    'publication': 'bbc',
    'city': 'Bangalore,IN',
    'src_currency': 'INR',
    'dest_currency': 'USD'
}

RSS_FEEDS = {
    'bbc': "http://feeds.bbci.co.uk/news/rss.xml",
    'cnn': "http://rss.cnn.com/rss/edition.rss",
    'fox': "http://feeds.foxnews.com/foxnews/latest"
}

WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=bf307c8864d572d293ca381b352778df"
CURRENCY_API_APP_ID = '3a6d63ef7bff4792882d7971f16a42aa'
CURRENCY_API_URL = "https://openexchangerates.org//api/latest.json?app_id=" + CURRENCY_API_APP_ID


@app.route("/")
def home():
    # Get headlines
    publication = request.args.get("publication")
    if not publication:
        publication = DEFAULTS['publication']
    articles = get_news(publication)

    # Get weather
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)

    # Get exchange rates
    src_currency = request.args.get('src_currency')
    dest_currency = request.args.get('dest_currency')

    if not src_currency:
        src_currency = DEFAULTS['src_currency']

    if not dest_currency:
        dest_currency = DEFAULTS['dest_currency']

    xchange_rate, currencies = get_rate(src_currency, dest_currency)

    return render_template('home.html',
                           articles=articles,
                           weather=weather,
                           src_currency=src_currency,
                           dest_currency=dest_currency,
                           xchange_rate=xchange_rate,
                           currencies=sorted(currencies))


def get_news(publication):
    if publication.lower() not in RSS_FEEDS:
        publication = DEFAULTS['publication']
    else:
        publication = publication.lower()

    feed = feedparser.parse(RSS_FEEDS[publication])

    return feed['entries']


def get_weather(city):
    city = requests.utils.quote(city)
    url = WEATHER_API_URL.format(city)
    data = requests.get(url).json()
    weather = None
    if data.get("weather"):
        weather = {
            "description": data["weather"][0]["description"],
            "temperature": data["main"]["temp"],
            "city": data["name"],
            "country": data["sys"]["country"]
        }
    return weather


def get_rate(src_currency, dest_currency):
    currency_data = requests.get(CURRENCY_API_URL).json()['rates']
    # print(currency_data)

    print(src_currency, dest_currency)

    src_crncy_xchange_rate_against_usd = currency_data[src_currency.upper()]
    dest_crncy_xchange_rate_against_usd = currency_data[dest_currency.upper()]
    xchange_rate = dest_crncy_xchange_rate_against_usd / src_crncy_xchange_rate_against_usd
    return (xchange_rate, currency_data.keys())


if __name__ == '__main__':
    app.run(port=5000, debug=True)
