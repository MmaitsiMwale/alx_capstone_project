from flask import Flask, render_template, request, abort, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import json
from urllib.parse import quote_plus

# get db pswd
with open('config.json', 'r') as f:
    config = json.load(f)

pswd = config.get('DB_PASSWORD')

encrypted_pswd = quote_plus(pswd)
app = Flask(__name__)

# initialize db and credentials
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://ed:{encrypted_pswd}@localhost/RecipeFinder'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# create model DB
class RecipeReviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.String(255), nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    def __repr__(self) -> str:
        return f'<Rating {self.rating}'


# Store Reviews

def insert_review(recipe_id, user_id, review_text, rating):
    new_review = RecipeReviews(recipe_id=recipe_id, user_id=user_id,
                               review_text=review_text, rating=rating)
    db.session.add(new_review)
    db.session.commit()

# fetch reviews by recipe_id


def fetch_reviews_by_recipe_id(recipe_id):
    return RecipeReviews.query.filter_by(recipe_id=recipe_id).all()


# Your Edamam API credentials here
APP_ID = "54dabdbd"
APP_KEY = "e7bf8594d6c614aea78e84528813c80a"
API_URL = "https://api.edamam.com/api/recipes/v2/"

# Global variable to hold favorite recipes.
favorite_recipes = []


# Function to fetch recipes from Edamam API


def fetch_recipes(query):
    url = f"https://api.edamam.com/api/recipes/v2?type=public&q={query}&app_id={APP_ID}&app_key={APP_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


# Home Page
@app.route('/', methods=['GET'])
def index():
    url = f"https://api.edamam.com/api/recipes/v2?type=public&q=random&app_id={APP_ID}&app_key={APP_KEY}&from=0&to=6"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'hits' not in data:
            return render_template('index.html', featured_recipes=None)

        featured_recipes = [hit['recipe'] for hit in data['hits']]
        return render_template('index.html', featured_recipes=featured_recipes)
    except requests.RequestException as e:
        print(f"An error occurred while fetching random recipes: {e}")
        return render_template('index.html', featured_recipes=None)

# Search Page


@app.route('/search')
def search():
    query = request.args.get('query')
    if query:
        data = fetch_recipes(query)
        return render_template('search.html', data=data)
    return render_template('search.html')


# Recipe Details Page
@app.route('/recipe_details', defaults={'recipe_id': None})
@app.route('/recipe_details/<string:recipe_id>')
def recipe_details(recipe_id):
    url = f"https://api.edamam.com/api/recipes/v2/{recipe_id}?type=public&app_id={APP_ID}&app_key={APP_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        # convert response to dict like structure
        data = response.json()
        # abort if recipe is not found in response
        if 'recipe' not in data:
            abort(404, description="Recipe details not found")

        # Fetch reviews for this recipe from the database
        reviews = fetch_reviews_by_recipe_id(recipe_id)

        return render_template('recipe_details.html', recipe_details=data['recipe'], reviews=reviews)

    except requests.RequestException as e:
        print(f"An error occurred while fetching recipe details: {e}")
        abort(500, description="Internal Server Error")

# functionality to add recipe to favorites


@app.route('/add_to_favorites/<string:recipe_id>', methods=['POST'])
def add_to_favorites(recipe_id):
    if recipe_id not in favorite_recipes:
        favorite_recipes.append(recipe_id)
    return redirect(url_for('favorites'))

# functionality to remove recipe to favorites


@app.route('/remove_from_favorites/<string:recipe_id>', methods=['POST'])
def remove_from_favorites(recipe_id):
    if recipe_id in favorite_recipes:
        favorite_recipes.remove(recipe_id)
    return redirect(url_for('favorites'))

# Favorite Recipes Page


@app.route('/favorites', methods=['GET'])
def favorites():
    # Create an empty list to hold the favorite recipe objects
    favorite_recipe_objects = []

    # Loop through the favorite_recipes list to fetch each recipe by its ID
    for recipe_id in favorite_recipes:
        url = f"https://api.edamam.com/api/recipes/v2/{recipe_id}?type=public&app_id={APP_ID}&app_key={APP_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if 'recipe' in data:
                favorite_recipe_objects.append(data['recipe'])
        except requests.RequestException as e:
            print(f"An error occurred while fetching a favorite recipe: {e}")

    # Render the favorites.html template and pass in the list of favorite recipe objects
    return render_template('favorites.html', favorite_recipes=favorite_recipe_objects)


@app.route("/rate_recipe/<string:recipe_id>", methods=["POST"])
def rate_recipe(recipe_id):
    rating = request.form.get("rating")
    review_text = request.form.get("review_text")
    user_id = "some_user_id"  # default a user_id for dev purposes
    if not rating:
        return abort(400, "Rating is required.")

    try:
        # Using int because your model defines rating as Integer
        rating = int(rating)
    except ValueError:
        return abort(400, "Invalid rating value.")

    if rating < 1 or rating > 5:
        return abort(400, "Rating must be between 1 and 5.")

    try:
        insert_review(recipe_id, user_id, review_text, rating)
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred while adding the rating: {e}")
        return abort(500, "Internal Server Error")

    return redirect(url_for("recipe_details", recipe_id=recipe_id))

# My Shopping List Page


@app.route('/shopping_list')
def shopping_list():
    # Will implement this function later
    return render_template('shopping_list.html')


if __name__ == '__main__':
    app.run(debug=True)
