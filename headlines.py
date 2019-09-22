import feedparser
import json
import requests
import datetime

from flask import Flask
from flask import render_template
from flask import request
from flask import make_response

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
    publication = get_value_with_fallback('publication')
    articles = get_news(publication)

    # Get weather
    city = get_value_with_fallback('city')
    weather = get_weather(city)

    # Get exchange rates
    src_currency = get_value_with_fallback('src_currency')
    dest_currency = get_value_with_fallback('dest_currency')

    xchange_rate, currencies = get_rate(src_currency, dest_currency)

    template = render_template('home.html', articles=articles, weather=weather, src_currency=src_currency,
                               dest_currency=dest_currency, xchange_rate=xchange_rate,
                               publications=sorted(RSS_FEEDS.keys()), currencies=sorted(currencies))
    response = make_response(template)

    # Set Cookies
    expiry = datetime.datetime.now() + datetime.timedelta(days=30)
    response.set_cookie("publication", publication, expires=expiry)
    response.set_cookie("city", city, expires=expiry)
    response.set_cookie("src_currency", src_currency, expires=expiry)
    response.set_cookie("dest_currency", dest_currency, expires=expiry)
    return response


def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]


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
    app.run(host='0.0.0.0', port=5000, debug=True)
