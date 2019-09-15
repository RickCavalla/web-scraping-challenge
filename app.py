from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo

# import our Mars scraping library
import scrape_mars

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

# Or set inline
# mongo = PyMongo(app, uri="mongodb://localhost:27017/craigslist_app")

# home route will just find the single Mongo collection
# of our mars data and pass that to index page
@app.route("/")
def index():
    mars = mongo.db.mars.find_one()
    return render_template("index.html", mars=mars)

# scrape route will be called by button on index page.
# it will pull all the Mars data from numerous web pages
# and return it all as a single collection
# that gets written to Mongo.
# then home route gets re-called to render with newly
# scraped data
@app.route("/scrape")
def scraper():
    mars = mongo.db.mars
    mars_data = scrape_mars.scrape()
    mars.update({}, mars_data, upsert=True)
    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(debug=True)