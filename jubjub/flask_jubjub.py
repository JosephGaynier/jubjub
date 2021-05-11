import os
from flask import Flask, render_template
from flask import request
from flask import redirect, url_for
from flask import session
from flask.templating import render_template_string
from forms import RegisterForm, LoginForm, SearchForm
from datetime import date, datetime
from database import db
from models import Event as Event
from models import User as User
from models import RsvpData as RsvpData
import bcrypt
from re import search

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jubjub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SE3155'

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/events/<event_id>')
def get_event(event_id):
    if session.get('user'):
        my_event = db.session.query(Event).filter_by(id=event_id).one()
        return render_template('event.html', event=my_event, user=session['user'])
    else:
        return redirect(url_for('login'))


@app.route('/events/new', methods=['GET', 'POST'])
def new_event():
    if session.get('user'):
        if request.method == 'POST':
            name = request.form['name']
            location = request.form['location']
            description = request.form['description']
            color = request.form['color']
            if 'is_public' in request.form:
                is_public = True
            else:
                is_public = False

            start_date = datetime.strptime(request.form['start_date'], '%m/%d/%y %H:%M:%S')
            end_date = datetime.strptime(request.form['end_date'], '%m/%d/%y %H:%M:%S')

            newEntry = Event(name, start_date, end_date, location, description, color, is_public, session['user_id'])
            newRSVPEntry = RsvpData(newEntry.id, session['user_id'])
            db.session.add(newEntry)
            db.session.add(newRSVPEntry)
            db.session.commit()
            return redirect(url_for('get_events'))
        else:
            return render_template('new.html', user=session['user'])
    else:
        return redirect(url_for('login'))


@app.route('/events/edit/<event_id>', methods=['GET', 'POST'])
def update_event(event_id):
    if session.get('user'):
        if request.method == 'POST':
            event = db.session.query(Event).filter_by(id=event_id).one()
            event.name = request.form['name']
            event.location = request.form['location']
            event.description = request.form['description']
            event.color = request.form['color']
            if 'is_public' in request.form:
                event.is_public = True
            else:
                event.is_public = False
            event.start_date = date.today()
            event.end_date = date.today()
            db.session.commit()
            return redirect(url_for('get_events'))
        else:
            my_event = db.session.query(Event).filter_by(id=event_id).one()
            return render_template('new.html', event=my_event, user=session['user'])
    else:
        return redirect(url_for('login'))


@app.route('/events/delete/<event_id>', methods=['POST'])
def delete_event(event_id):
    if session.get('user'):
        my_event = db.session.query(Event).filter_by(id=event_id).one()
        db.session.delete(my_event)
        db.session.commit()
        return redirect(url_for('get_events'))
    else:
        return redirect(url_for('login'))

@app.route('/events/invite/<event_id>', methods=['POST'])
def invite_user(event_id):
    if session.get('user'):
        my_event = db.session.query(Event).filter_by(id=event_id).one()
        db.session.delete(my_event)
        db.session.commit()
        return redirect(url_for('get_events'))
    else:
        return redirect(url_for('login'))

def accept_invite(event_id):
    if session.get('user'):
        if request.method == 'POST':
            event = db.session.query(Event).filter_by(id=event_id).one()
            name = request.form['name']
            location = request.form['location']
            description = request.form['description']
            color = request.form['color']
            if 'is_public' in request.form:
                is_public = True
            else:
                is_public = False

            start_date = datetime.strptime(request.form['start_date'], '%m/%d/%y %H:%M:%S')
            end_date = datetime.strptime(request.form['end_date'], '%m/%d/%y %H:%M:%S')

            newEntry = Event(name, start_date, end_date, location, description, color, is_public, session['user_id'])
            db.session.add(newEntry)
            db.session.commit()
            return redirect(url_for('get_events'))
        else:
            return render_template('new.html', user=session['user'])
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        password_hash = bcrypt.hashpw(
            request.form['password'].encode('utf-8'), bcrypt.gensalt())
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        new_record = User(first_name, last_name,
                          request.form['email'], password_hash)
        db.session.add(new_record)
        db.session.commit()
        session['user'] = first_name
        the_user = db.session.query(User).filter_by(
            email=request.form['email']).one()
        session['user_id'] = the_user.id

        return redirect(url_for('get_events'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        the_user = db.session.query(User).filter_by(
            email=request.form['email']).one()
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), the_user.password):
            session['user'] = the_user.first_name
            session['user_id'] = the_user.id
            return redirect(url_for('get_events'))
        login_form.password.errors = ["Incorrect username or password."]
        return render_template("login.html", form=login_form)
    else:
        return render_template("login.html", form=login_form)


@app.route('/')
@app.route('/events', methods=['POST', 'GET'])
def get_events():
    if session.get('user'):
        if request.method == 'POST':
            search_form = SearchForm()
            searchText = request.form['search']
            my_events = db.session.query(Event).filter_by(
                user_id=session['user_id']).all()
            
            events_to_display = []
            for event in my_events:
                if search(searchText.lower(), event.name.lower()):
                    events_to_display.append(event)
            return render_template('events.html', events=events_to_display, user=session['user'], form=search_form)
        else:
            form = SearchForm()
            my_events = db.session.query(Event).filter_by(
                user_id=session['user_id']).all()
            return render_template('events.html', events=my_events, user=session['user'], form=form)
    else:
        return redirect(url_for('login'))

@app.route('/event_requests', methods=['POST', 'GET'])
def get_event_requests():
    if session.get('user'):
        if request.method == 'POST':
            search_form = SearchForm()
            searchText = request.form['search']
            my_events = db.session.query(Event).filter_by(
                user_id=session['user_id']).all()
            
            events_to_display = []
            for event in my_events:
                if search(searchText, event.name):
                    events_to_display.append(event)
            return render_template('eventRequests.html', events=events_to_display, user=session['user'], form=search_form)
        else:
            form = SearchForm()
            my_events = db.session.query(Event).filter_by(
                user_id=session['user_id']).all()
            return render_template('eventRequests.html', events=my_events, user=session['user'], form=form)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    if session.get('user'):
        session.clear()
    return redirect(url_for('login'))


@app.route('/profile')
def get_profile():
    if session.get('user'):
        curr_user = db.session.query(User).filter_by(first_name=session['user']).one()
        return render_template('profile.html', user=curr_user)
    else:
        return redirect(url_for('login'))


app.run(host=os.getenv('IP', '127.0.0.1'), port=int(
    os.getenv('PORT', 5000)), debug=True)
