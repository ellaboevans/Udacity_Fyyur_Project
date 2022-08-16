## Fyyur

### Introduction

A website for booking musical venues and musicians called Fyyur makes it easier for venues to find and book local performers for performances. This website enables venue owners to list concerts with artists, list new artists and venues, and discover new artists and venues. On the Udacity Full Stack Web Development nanodegree program, this was my first project.

My job was to connect to a PostgreSQL database for storing, accessing, and producing data about artists and venues on the Fyyur website in order to build up the data models that would power the API endpoints for the site.


### Overview

This app was nearly complete. It was only missing one thing … real data! While the views and controllers were defined in this application, it was missing models and model interactions to be able to store retrieve, and update data from a database. By the end of this project, I had a fully functioning site that was at least capable of doing the following, if not more, using a PostgreSQL database:

- creating new venues, artists, and creating new shows.
- searching for venues and artists.
- learning more about a specific artist or venue.

### Tech Stack

The tech stack for this project was:

- **SQLAlchemy ORM** to be the ORM library of choice
- **PostgreSQL** as the database of choice
- **Python3** and **Flask** as our server language and server framework
- **Flask-Migrate** for creating and running schema migrations
- **HTML**, **CSS**, and **Javascript** with [Bootstrap 3](https://getbootstrap.com/docs/3.4/customize/) for the website's frontend

### Main Files: Project Structure

```
├── README.md
├── app.py *** the main driver of the app. Includes your SQLAlchemy models.
                  "python app.py" to run after installing dependences
├── config.py *** Database URLs, CSRF generation, etc
├── error.log
├── forms.py *** Forms
├── requirements.txt *** The dependencies to be installed with "pip3 install -r requirements.txt"
├── static
│   ├── css
│   ├── font
│   ├── ico
│   ├── img
│   └── js
└── templates
    ├── errors
    ├── forms
    ├── layouts
    └── pages
```

Overall:

- Models are located in the `MODELS` section of `app.py`.
- Controllers are also located in `app.py`.
- The web frontend is located in `templates/`, which builds static assets deployed to the web server at `static/`.
- Web forms for creating data are located in `form.py`

### Development Setup

First, [install Flask](http://flask.pocoo.org/docs/1.0/installation/#install-flask) if you haven't already.

```
$ cd ~
$ sudo pip3 install Flask
```

To start and run the local development server,

1. Initialize and activate a virtualenv:

```
$ cd YOUR_PROJECT_DIRECTORY_PATH/
$ virtualenv --no-site-packages env
$ source env/bin/activate
```

2. Install the dependencies:

```
$ pip install -r requirements.txt
```

3. Run the development server:

```
$ export FLASK_APP=myapp
$ export FLASK_ENV=development # enables debug mode
$ python3 app.py
```

4. Navigate to Home page [http://localhost:5000](http://localhost:5000)
