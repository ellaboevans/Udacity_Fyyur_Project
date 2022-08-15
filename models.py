from sqlalchemy import String, ARRAY
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
db = SQLAlchemy()


def db_setup(app):

    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    return db



class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    artist_genre_table = db.Table('artist_genre_table',
                                  db.Column('genres_id', db.Integer, db.ForeignKey(
                                      'genres.id'), primary_key=True),
                                  db.Column('artists_id', db.Integer, db.ForeignKey(
                                      'artists.id'), primary_key=True)
                                  )

    venue_genre_table = db.Table('venue_genre_table',
                                 db.Column('genres_id', db.Integer, db.ForeignKey(
                                     'genres.id'), primary_key=True),
                                 db.Column('venues_id', db.Integer, db.ForeignKey(
                                     'venues.id'), primary_key=True)
                                 )


artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'),
                      nullable=False)


def __repr__(self, name, artists_genre_table, venue_genre_table):
    self.name = name
    self.artists_genre_table = artists_genre_table
    self.venue_genre_table = venue_genre_table


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    genres = db.Column(ARRAY(String))

    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))

    shows = db.relationship('Show', backref='venue_list', lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # genres = db.Column(db.String(120))
    genres = db.relationship('Genre', backref='artist', lazy=True)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    genres = db.Column(ARRAY(String))

    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))

    shows = db.relationship('Show', backref='artist_list', lazy=True)

    def __repr__(self):
        return f'<Artist: {self.id} {self.name}>'


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)

    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), nullable=False)

    def __repr__(self):
        return f'<Show: {self.id} {self.start_time}>'