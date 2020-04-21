from flask_login import UserMixin

from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


class Race(db.Model):
    __tablename__ = 'race'
    __table_args__ = (
        db.UniqueConstraint('name', 'race', 'time'),
    )

    id = db.Column(db.BigInteger, primary_key=True)
    pos = db.Column(db.Integer)
    name = db.Column(db.String)
    race = db.Column(db.String)
    time = db.Column(db.Interval)
    sex = db.Column(db.String)
    age = db.Column(db.Numeric)
    cat = db.Column(db.String)
    distance_km = db.Column(db.Float)
    race_year = db.Column(db.Integer)

    def __repr__(self):
        return '<Race %r>' % self.id
