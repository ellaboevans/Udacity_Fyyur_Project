#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment

import logging
from logging import Formatter, FileHandler

from forms import *
import os
import sys
from datetime import datetime

from operator import itemgetter  # for sorting lists of tuples
import collections
from models import db_setup, Venue, Show, Artist




#
collections.Callable = collections.abc.Callable
# ----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

db = db_setup(app)



#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@ app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@ app.route('/venues')
def venues():
    # TODO: replace with real venues data.

    venues = Venue.query.all()

    data = []

    cities_states = set()
    for venue in venues:
        cities_states.add((venue.city, venue.state))

    cities_states = list(cities_states)

    cities_states.sort(key=itemgetter(1, 0))

    now = datetime.now()

    # Now iterate over the unique values to seed the data dictionary with city/state locations
    for loc in cities_states:
        # For this location, see if there are any venues there, and add if so
        venues_list = []
        for venue in venues:
            if (venue.city == loc[0]) and (venue.state == loc[1]):

                # If we've got a venue to add, check how many upcoming shows it has
                venue_shows = Show.query.filter_by(venue_id=venue.id).all()
                num_upcoming = 0
                for show in venue_shows:
                    if show.start_time > now:
                        num_upcoming += 1

                venues_list.append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": num_upcoming
                })

        # After all venues are added to the list for a given location, add it to the data dictionary
        data.append({
            "city": loc[0],
            "state": loc[1],
            "venues": venues_list
        })

    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    # data = [{
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "venues": [{
    #         "id": 1,
    #         "name": "The Musical Hop",
    #         "num_upcoming_shows": 0,
    #     }, {
    #         "id": 3,
    #         "name": "Park Square Live Music & Coffee",
    #         "num_upcoming_shows": 1,
    #     }]
    # }, {
    #     "city": "New York",
    #     "state": "NY",
    #     "venues": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }]
    return render_template('pages/venues.html', areas=data)


@ app.route('/venues/search', methods=['POST'])
def search_venues():

    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    search_term = request.form.get('search_term', '')

    # Use filter, not filter_by when doing LIKE search (i=insensitive to case)
    # Wildcards search before and after
    venues = Venue.query.filter(
        Venue.name.ilike('%' + search_term + '%')).all()
    print(venues)
    venue_list = []
    now = datetime.now()
    for venue in venues:
        venue_shows = Show.query.filter_by(venue_id=venue.id).all()
        num_upcoming = 0
        for show in venue_shows:
            if show.start_time > now:
                num_upcoming += 1

        venue_list.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_upcoming  # FYI, template does nothing with this
        })
        # seach for Hop should return "The Musical Hop".
        # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
        response = {
            "count": len(venues),
            "data": venue_list
        }

        # response = {
        #     "count": 1,
        #     "data": [{
        #         "id": 2,
        #         "name": "The Dueling Pianos Bar",
        #         "num_upcoming_shows": 0,
        #     }]
        # }

        return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    data = {}
    # shows the venue page with the given venue_id

    # Get all the data from the DB and populate the data dictionary (context)
    # venue = Venue.query.filter_by(id=venue_id).one_or_none()
    # Returns object by primary key, or None
    try:

        requested_venue = Venue.query.get(venue_id)

        if requested_venue is None:
            return not_found_error(404)

        genres = []
        for item in requested_venue.genres:
            genres.append(item)

        shows = Show.query.filter_by(venue_id=venue_id)

        today = datetime.now()

        raw_past_shows = shows.filter(Show.start_time > today).all()
        past_shows = []

        for show in raw_past_shows:
            artist = Artist.query.get(show.artist_id)
            show_data = {

                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }
            past_shows.append(show_data)

        raw_upcoming_shows = shows.filter(Show.start_time >= today). all()
        upcoming_shows = []
        for show in raw_upcoming_shows:
            artist = Artist.query.get(show.artist_id)
            show_data = {

                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }
            upcoming_shows.append(show_data)

        data = {
            "id": requested_venue.id,
            "name": requested_venue.name,
            "genres": requested_venue.genres,
            "address": requested_venue.address,
            "city": requested_venue.city,
            "state": requested_venue.state,
            "phone": requested_venue.phone,
            # "website": requested_venue.website,
            "facebook_link": requested_venue.facebook_link,
            "seeking_talent": requested_venue.seeking_talent,
            "image_link": requested_venue.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }

    except Exception as e:
        print(sys.exc_info())
        flash("Something went wrong. Please try again. " + str(e))

    finally:
        db.session.close()

    return render_template('pages/show_venue.html', venue=data)

    # data1 = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #     "past_shows": [{
    #         "artist_id": 4,
    #         "artist_name": "Guns N Petals",
    #         "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "genres": ["Classical", "R&B", "Hip-Hop"],
    #     "address": "335 Delancey Street",
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "914-003-1132",
    #     "website": "https://www.theduelingpianos.com",
    #     "facebook_link": "https://www.facebook.com/theduelingpianos",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    #     "address": "34 Whiskey Moore Ave",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "415-000-1234",
    #     "website": "https://www.parksquarelivemusicandcoffee.com",
    #     "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "past_shows": [{
    #         "artist_id": 5,
    #         "artist_name": "Matt Quevedo",
    #         "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [{
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 1,
    # }
    # data = list(filter(lambda d: d['id'] ==
    #                    venue_id, [data1, data2, data3]))[0]


#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False

    # we have to pass request.form to VenueForm
    # venueform help to validate the data sent
    # to the controller
    form = VenueForm(request.form)

    try:
        # next we have to check if the data is valid
        if form.validate():
            # if true then we create venue
            # next we hvae to access the data from the form

            # go ahead and change the
            # continue it ok sure
            venues = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                website_link=form.website_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data

            )

            # now we have to save in to the database
            # we call on db object to create the connection
            db.session.add(venues)
            db.session.commit()
        else:
            error = True

    except Exception as e:
        print(str(e))
        # we then have to rollback the change when encounter issue
        print(sys.exc_info())
        db.session.rollback()

    finally:
        # finally we have to close the transaction

        db.session.close()

    if not error:
        # on successful db insert, flash success

        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

    return render_template('pages/home.html')


@ app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # Deletes a venue based on AJAX call from the venue page
    venue = Venue.query.get(venue_id)
    if not venue:
        # User somehow faked this call, redirect home
        return redirect(url_for('index'))
    else:
        error_on_delete = False
        # Need to hang on to venue name since will be lost after delete
        venue_name = venue.name
        try:
            db.session.delete(venue)
            db.session.commit()
        except:
            error_on_delete = True
            db.session.rollback()
        finally:
            db.session.close()
        if error_on_delete:
            flash(f'An error occurred deleting venue {venue_name}.')
            print("Error in delete_venue()")
            abort(500)
        else:
            flash(f'Successfully removed venue {venue_name}')
            return redirect(url_for('venues'))
            # return jsonify({
            #  'deleted': True,
            #   'url': url_for('venues')
            # })


#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    artists = Artist.query.order_by(Artist.name).all()

    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })

    # data = [{
    #     "id": 4,
    #     "name": "Guns N Petals",
    # }, {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    # }, {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    # }]
    return render_template('pages/artists.html', artists=data)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    search_term = request.form.get('search_term', '').strip()

    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    artists = Artist.query.filter(
        Artist.name.ilike('%' + search_term + '%')).all()
    # search for "band" should return "The Wild Sax Band".
    artist_list = []
    now = datetime.now()
    for artist in artists:
        artist_shows = Show.query.filter_by(artist_id=artist.id).all()
        num_upcoming = 0
        for show in artist_shows:
            if show.start_time > now:
                num_upcoming += 1

        artist_list.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": num_upcoming  # FYI, template does nothing with this
        })

    response = {
        "count": len(artists),
        "data": artist_list
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    data = {}

    try:
        requested_artist = Artist.query.get(artist_id)

        if requested_artist is None:
            return not_found_error(404)

        genres = requested_artist.genres

        shows = Show.query.filter_by(artist_id=artist_id)

        today = datetime.now()

        raw_past_shows = shows.filter(Show.start_time < today).all()
        past_shows = []
        for show in raw_past_shows:
            venue = Venue.query.get(show.venue_id)
            show_data = {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": str(show.start_time),
            }
            past_shows.append(show_data)

        raw_upcoming_shows = shows.filter(Show.start_time >= today).all()
        upcoming_shows = []
        for show in raw_upcoming_shows:
            venue = Venue.query.get(show.venue_id)
            show_data = {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": str(show.start_time),
            }
            upcoming_shows.append(show_data)

        data = {
            "id": requested_artist.id,
            "name": requested_artist.name,
            "genres": requested_artist.genres,
            "city": requested_artist.city,
            "state": requested_artist.state,
            "phone": requested_artist.phone,
            "seeking_venue": False,
            "facebook_link": requested_artist.facebook_link,
            "image_link": requested_artist.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }

    except Exception as e:
        print(sys.exc_info())
        flash(f"Something went wrong. Please try again.: {e}")

    finally:
        db.session.close()

    return render_template("pages/show_artist.html", artist=data)

    # data1 = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "past_shows": [{
    #         "venue_id": 1,
    #         "venue_name": "The Musical Hop",
    #         "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    #     "genres": ["Jazz"],
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "300-400-5000",
    #     "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "past_shows": [{
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    #     "genres": ["Jazz", "Classical"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "432-325-5432",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [{
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 3,
    # }
    # data = list(filter(lambda d: d['id'] ==
    #                    artist_id, [data1, data2, data3]))[0]

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # Get the existing artist from the database
    # Returns object based on primary key, or None.  Guessing get is faster than filter_by
    artist = Artist.query.get(artist_id)
    if not artist:
        # User typed in a URL that doesn't exist, redirect home
        return redirect(url_for('index'))
    else:
        # Otherwise, valid artist.  We can prepopulate the form with existing data like this.
        # Prepopulate the form with the current values.  This is only used by template rendering!
        form = ArtistForm(obj=artist)

    # genres needs to be a list of genre strings for the template
    genres = [genre for genre in artist.genres]

    artist = {
        "id": artist_id,
        "name": artist.name,
        "genres": genres,
        # "address": artist.address,
        "city": artist.city,
        "state": artist.state,
        # Put the dashes back into phone number
        "phone": (artist.phone[:3] + '-' + artist.phone[3:6] + '-' + artist.phone[6:]),
        # "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link
    }

    # artist = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    # }
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)
    artist_data = Artist.query.get(artist_id)
    if artist_data:
        if form.validate():
            seeking_venue = False
            seeking_description = ''
            if 'seeking_venue' in request.form:
                seeking_venue = request.form['seeking_venue'] == 'y'
            if 'seeking_description' in request.form:
                seeking_description = request.form['seeking_description']
            setattr(artist_data, 'name', request.form['name'])
            setattr(artist_data, 'genres', request.form.getlist('genres'))
            setattr(artist_data, 'city', request.form['city'])
            setattr(artist_data, 'state', request.form['state'])
            setattr(artist_data, 'phone', request.form['phone'])
            setattr(artist_data, 'website_link', request.form['website_link'])
            setattr(artist_data, 'facebook_link', request.form['facebook_link'])
            setattr(artist_data, 'image_link', request.form['image_link'])
            setattr(artist_data, 'seeking_description', seeking_description)
            setattr(artist_data, 'seeking_venue', seeking_venue)
            
            return redirect(url_for('show_artist', artist_id=artist_id))
        else:
            print(form.errors)
    return render_template('errors/404.html'), 404

@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    
    venue = Venue.query.get(venue_id)
    if not venue:
        # User typed in a URL that doesn't exist, redirect home
        return redirect(url_for('index'))
    else:
        # Otherwise, valid venue.  We can prepopulate the form with existing data like this:
        form = VenueForm(obj=venue)

    # Prepopulate the form with the current values.  This is only used by template rendering!

    # genres needs to be a list of genre strings for the template
    genres = [genre for genre in venue.genres]

    venue = {
        "id": venue_id,
        "name": venue.name,
        "genres": genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        # Put the dashes back into phone number
        "phone": (venue.phone[:3] + '-' + venue.phone[3:6] + '-' + venue.phone[6:]),
        # "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
    }

    # venue = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    # }
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # Much of this code same as /venue/create view.

    form = VenueForm(request.form)

    name = form.name.data,
    city = form.city.data,
    state = form.state.data
    address = form.address.data,
    phone = form.phone.data,
    genres =form.genres.data,
    seeking_talent = form.seeking_talent.data,
    seeking_description = form.seeking_description.data,
    image_link = form.image_link.data,
    website = form.website_link.data,
    facebook_link = form.facebook_link.data

    # Redirect back to form if errors in form validation
    if not form.validate():
        # flash(form.errors)
        return redirect(url_for('edit_venue_submission', venue_id=venue_id))

    else:
        error_in_update = False

        # Insert form data into DB
        try:
            # First get the existing venue object
            venue = Venue.query.get(venue_id)
            # venue = Venue.query.filter_by(id=venue_id).one_or_none()

            # Update fields
            venue.name = name
            venue.city = city
            venue.state = state
            venue.address = address
            venue.phone = phone

            venue.seeking_talent = seeking_talent
            venue.seeking_description = seeking_description
            venue.image_link = image_link
            venue.website = website
            venue.facebook_link = facebook_link

            # First we need to clear (delete) all the existing genres off the venue otherwise it just adds them

            # For some reason this didn't work! Probably has to do with flushing/lazy, etc.
            # for genre in venue.genres:
            #     venue.genres.remove(genre)

            # venue.genres.clear()  # Either of these work.
            venue.genres = []

            # genres can't take a list of strings, it needs to be assigned to db objects
            # genres from the form is like: ['Alternative', 'Classical', 'Country']
            for genre in genres:
                # Throws an exception if more than one returned, returns None if none
                fetch_genre = Genre.query.filter_by(name=genre).one_or_none()
                if fetch_genre:
                    # if found a genre, append it to the list
                    venue.genre.append(fetch_genre)

                else:
                    # fetch_genre was None. It's not created yet, so create it
                    new_genre = Genre(name=genre)
                    db.session.add(new_genre)
                    # Create a new Genre item and append it
                    venue.genre.append(new_genre)

            # Attempt to save everything
                    db.session.commit()
                    db.session.no_autoflush()
        except Exception as e:
            error_in_update = True
            print(f'Exception "{e}" in edit_venue_submission()')
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        if not error_in_update:
            # on successful db update, flash success
            flash('Venue ' + request.form['name'] +
                  ' was successfully updated!')
            return redirect(url_for('show_venue', venue_id=venue_id))
        else:
            flash('An error occurred. Venue ' +
                  request.form.get("name") + ' could not be updated.')

            print("Error in edit_venue_submission()")
            abort(500)

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    error = False

    # we have to pass request.form to VenueForm
    # artistform help to validate the data sent
    # to the controller
    form = ArtistForm(request.form)

    try:
        # next we have to check if the data is valid
        if form.validate():
            # if true then we create artists
            # next we have to access the data from the form

            # go ahead and change the
            # continue it ok sure
            artists = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                website_link=form.website_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data

            )

            # now we have to save in to the database
            # we call on db object to create the connection
            db.session.add(artists)
            db.session.commit()
        else:
            error = True

    except Exception as e:
        print(str(e))
        # we then have to rollback the change when encounter issue
        db.session.rollback()
    finally:
        # finally we have to close the transaction
        db.session.close()

    if not error:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
        # TODO: on unsuccessful db insert, flash an error instead.

        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')

        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

    return render_template('pages/home.html')


@ app.route('/artists/<artist_id>/delete', methods=['GET'])
def delete_artist(artist_id):
    
    # Deletes a artist based on AJAX call from the artist page
    artist = Artist.query.get(artist_id)
    if not artist:
        # User somehow faked this call, redirect home
        return redirect(url_for('index'))
    else:
        error_on_delete = False
        # Need to hang on to artist name since will be lost after delete
        artist_name = artist.name
        try:
            db.session.delete(artist)
            db.session.commit()
        except:
            error_on_delete = True
            db.session.rollback()
        finally:
            db.session.close()
        if error_on_delete:
            flash(f'An error occurred deleting artist {artist_name}.')
            print("Error in delete_artist()")
            abort(500)
        else:
            flash(f'Successfully removed artist {artist_name}')
            # return redirect(url_for('artists'))
            return jsonify({
                'deleted': True,
                'url': url_for('artists')
            })


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    # displays list of shows at /shows

    data = []

    try:
        shows = Show.query.all()

        for show in shows:
            venue_id = show.venue_id
            artist_id = show.artist_id
            artist = Artist.query.get(artist_id)

            each_show_data = {
                "venue_id": venue_id,
                "venue_name": Venue.query.get(venue_id).name,
                "artist_id": Artist.query.get(artist_id).name,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }

            data.append(each_show_data)

    except:
        db.session.rollback()
        print(sys.exc_info())
        flash("Something went wrong, please try again.")

    finally:
        db.session.close()
    return render_template("pages/shows.html", shows=data)

    # data = [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #    "artist_id": 4,
    #   "artist_name": "Guns N Petals",
    #      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #    "venue_name": "Park Square Live Music & Coffee",
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #   "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    # }]


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch

    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form

    form = ShowForm()

    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')

    error_in_insert = False

    try:
        new_show = Show(start_time=start_time,
                        artist_id=artist_id, venue_id=venue_id)
        db.session.add(new_show)
        db.session.commit()

    except Exception as e:
        error_in_insert = True
        print(f'Exception "{e} " in create_show_submission()')
        db.session.rollback()

    finally:
        db.session.close()

    if error_in_insert:

        flash(f'An error occured. Show could not be listed.')
        print("Error in create_show_submission")
    else:

        flash('Show was successfully listed!')

    return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
