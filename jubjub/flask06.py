import os
from flask import Flask, render_template
from flask import request
from flask import redirect, url_for
from flask import session
from flask.templating import render_template_string
from forms import RegisterForm, LoginForm, CommentForm
from datetime import date
from database import db
from models import Event as Event
from models import User as User
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jubjub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SE3155'

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
@app.route('/index')
def index():
    if session.get('user'):
        return render_template("index.html", user=session['user'])
    return render_template('index.html')


@app.route('/events')
def get_events():
    if session.get('user'):
        my_events = db.session.query(Event).filter_by(
            user_id=session['user_id']).all()
        return render_template('events.html', events=my_events, user=session['user'])
    else:
        return redirect(url_for('login'))


@app.route('/events/<event_id>')
def get_event(event_id):
    if session.get('user'):
        my_event = db.session.query(Event).filter_by(id=event_id).one()
        form = CommentForm()
        return render_template('event.html', event=my_event, user=session['user'], form=form)
    else:
        return redirect(url_for('login'))


@app.route('/events/new', methods=['GET', 'POST'])
def new_event():
    if session.get('user'):
        if request.method == 'POST':
            title = request.form['title']
            text = request.form['eventText']
            today = date.today()
            today = today.strftime("%m-%d-%Y")
            // Needs changed
            newEntry = Note(title, text, today, session['user_id'])
            db.session.add(newEntry)
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
            title = request.form['title']
            text = request.form['noteText']
            event = db.session.query(Event).filter_by(id=event_id).one()
            note.title = title
            note.text = text
            db.session.add(note)
            db.session.commit()
            return redirect(url_for('get_events'))
        else:
            my_note = db.session.query(Event).filter_by(id=event_id).one()
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


@app.route('/logout')
def logout():
    if session.get('user'):
        session.clear()
    return redirect(url_for('index'))

#remove?
@app.route('/notes/<note_id>/comment', methods=['POST'])
def new_comment(note_id):
    if session.get('user'):
        comment_form = CommentForm()
        # validate_on_submit only validates using POST
        if comment_form.validate_on_submit():
            # get comment data
            comment_text = request.form['comment']
            new_record = Comment(comment_text, int(
                note_id), session['user_id'])
            db.session.add(new_record)
            db.session.commit()

        return redirect(url_for('get_note', note_id=note_id))

    else:
        return redirect(url_for('login'))


app.run(host=os.getenv('IP', '127.0.0.1'), port=int(
    os.getenv('PORT', 5000)), debug=True)
