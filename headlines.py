import feedparser
from flask import Flask

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
@app.route("/<publication>")
def get_news(publication='bbc'):
    feed = feedparser.parse(rss_urls[publication])
    first_article = feed['entries'][0]
    return html_template.format(first_article.get('title'),
                                first_article.get('published'),
                                first_article.get('summary'))


if __name__ == '__main__':
    app.run(port=5000, debug=True)
