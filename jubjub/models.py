import datetime
from database import db


class User(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    first_name = db.Column("first_name", db.String(100))
    last_name = db.Column("last_name", db.String(100))
    email = db.Column("email", db.String(100))
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    events = db.relationship("Event", backref="user", lazy=True)

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.registered_on = datetime.date.today()


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    is_public = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, name, start_date, end_date, location, description, color, is_public, user_id):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.location = location
        self.description = description
        self.color = color
        self.date_posted = datetime.date.today()
        self.is_public = is_public
        self.user_id = user_id

class RsvpData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user= db.relationship("User", lazy=True)
    event= db.relationship("Event", lazy=True)

    def __init__(self, event_id, user_id):
        self.event_id = event_id
        self.user_id = user_id