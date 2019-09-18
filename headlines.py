import feedparser
from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

html_template = """
        <html>
            <body>
                <h1>Headlines</h1>
                <b>{0}</b> <br/>
                <em>{1}</em> <br/>
                <p>{2}</p> <br/>
            </body>
        </html>
       """

rss_urls = {
    'bbc': "http://feeds.bbci.co.uk/news/rss.xml",
    'cnn': "http://rss.cnn.com/rss/edition.rss",
    'fox': "http://feeds.foxnews.com/foxnews/latest"
}


@app.route("/")
def get_news():
    query = request.args.get("publication")

    if (not query) or (query.lower() not in rss_urls):
        publication = "bbc"
    else:
        publication = query.lower()

    feed = feedparser.parse(rss_urls[publication])
    return render_template('home.html', articles=feed['entries'])


if __name__ == '__main__':
    app.run(port=5000, debug=True)
