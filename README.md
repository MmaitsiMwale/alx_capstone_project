# Recipe Finder

## Table of Contents

1. [Introduction](#introduction)
2. [Objectives](#objectives)
3. [Dependencies](#dependencies)
4. [Installation and Setup](#installation-and-setup)
5. [Project Structure](#project-structure)
6. [Technical Depth](#technical-depth)
7. [Contributing](#contributing)
8. [License](#license)

## Introduction

Recipe Finder is a Flask-based web application that allows users to search and view recipes. Users can also leave reviews to recipes and add them to their favorites. Their reviews will be stored in a MySQL database for any downstream usage such as analysis, machine learning among others.

## Objectives

- To provide a user-friendly interface for recipe search.
- To integrate with external APIs for fetching recipe data.
- To store user preferences and history in a MySQL database.

## Dependencies

The project uses the following libraries and frameworks:

- Flask
- SQLAlchemy
- requests
- urllib
- json

## Installation and Setup

1. Clone the repository.
2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up the MySQL database.
4. Run the application:

    ```bash
    python app.py
    ```

## Project Structure

- `app.py`: Main application file.
- `requirements.txt`: Lists the project dependencies.
- `static`: Contains static files like CSS, images.
- `templates`: Contains HTML templates.

## Technical Depth

The project uses Flask as the web framework and SQLAlchemy for database interactions. It also uses the requests library for making HTTP requests and json for handling JSON data. The project connects to a MySQL database, with configurations for the database connection.

## Contributing

If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.

## License

MIT License.
