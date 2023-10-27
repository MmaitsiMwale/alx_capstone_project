from flask import Flask, render_template, request, abort, redirect, url_for
import requests
import json

app = Flask(__name__)

# Your Edamam API credentials here
APP_ID = "54dabdbd"
APP_KEY = "e7bf8594d6c614aea78e84528813c80a"
API_URL = "https://api.edamam.com/api/recipes/v2/"

# Global variable to hold favorite recipes.
# In a real-world application, this data should be saved in a database.
favorite_recipes = []

# Dictionary to store ratings. In a real-world application, this data should be saved in a database.
# The keys are recipe IDs, and the values are lists of ratings for that recipe.
recipe_ratings = {}

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
        data = response.json()

        if 'recipe' not in data:
            abort(404, description="Recipe details not found")

        return render_template('recipe_details.html', recipe_details=data['recipe'])
    except requests.RequestException as e:
        print(f"An error occurred while fetching recipe details: {e}")
        abort(500, description="Internal Server Error")


@app.route('/add_to_favorites/<string:recipe_id>', methods=['POST'])
def add_to_favorites(recipe_id):
    if recipe_id not in favorite_recipes:
        favorite_recipes.append(recipe_id)
    return redirect(url_for('favorites'))


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
    if not rating:
        return abort(400, "Rating is required.")

    rating = float(rating)
    if rating < 1 or rating > 5:
        return abort(400, "Rating must be between 1 and 5.")

    if recipe_id not in recipe_ratings:
        recipe_ratings[recipe_id] = []

    recipe_ratings[recipe_id].append(rating)
    return redirect(url_for("recipe_details", recipe_id=recipe_id))

# My Shopping List Page


@app.route('/shopping_list')
def shopping_list():
    # Will implement this function later
    return render_template('shopping_list.html')


if __name__ == '__main__':
    app.run(debug=True)
