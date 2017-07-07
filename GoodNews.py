import feedparser
import json
import urllib.request
import urllib.parse
import requests


from flask import Flask, render_template, request
app = Flask(__name__)
RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS = {'publication': 'bbc',
            'city': 'London,UK',
            'currency_from': 'GBP',
            'currency_to': 'USD'
            }


@app.route("/")
def home():
    # get customized headlines, based on user input or default
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    articles = get_news(publication)

    # get customized weather based on user input or default
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)
    # get customized currency based on user input or default
    currency_from = request.args.get("currency_from")
    if not currency_from:
        currency_from = DEFAULTS['currency_from']
    currency_to = request.args.get("currency_to")
    if not currency_to:
        currency_to = DEFAULTS['currency_to']
    rate, currencies = get_rate(currency_from, currency_to)
    return render_template("home.html", articles=articles, weather=weather,
                           currency_from=currency_from, currency_to=currency_to,
                           rate=rate, currencies=sorted(currencies))


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS["publication"]
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']


def get_weather(query):
    req_data = {'q': query,
                'units': 'metric',
                'appid': '1174124455418df40a5ed0adbb1a3fcb'}

    response = requests.get('http://api.openweathermap.org/data/2.5/weather', req_data)
    parsed = response.json()
    weather = None
    if parsed.get("weather"):
        weather = {"description": parsed["weather"][0]["description"],
                   "temperature": parsed["main"]["temp"],
                   "city": parsed["name"],
                   'country': parsed['sys']['country']
        }
    return weather


def get_rate(frm, to):
    req_data = {'app_id': '8aff5ea807f34a5f82375aebe6e0fbe9'}
    response = requests.get("https://openexchangerates.org//api/latest.json", req_data)
    parsed = response.json().get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return to_rate/frm_rate, parsed.keys()

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000, debug=True)