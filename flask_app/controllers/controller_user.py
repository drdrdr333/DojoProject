
from hashlib import new
from urllib import response
from flask import flash
import requests, os
import time
import datetime
from datetime import date
from flask import request, session, render_template, redirect
from flask_app.models import user
from flask_app.models import event
from flask_app import app
from flask_bcrypt import Bcrypt

bcrypt=Bcrypt(app)

# def event_notification(date, events):
#     event_notification = 0
    


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/create_user', methods=['POST'])
def create_user():

    if not user.User.validate_user(request.form):
        return redirect('/')
    

    pw_hash = bcrypt.generate_password_hash(request.form['password'])

    data = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'password': pw_hash,
        'birth_date': request.form['birth_date']
    }

    user.User.add_user(data)
    the_user = user.User.get_newest_user()
   
    session['user_id'] = the_user.id

    if session['user_id'] == the_user.id:
        flash(f"{the_user.first_name} {the_user.last_name} created successfully.", 'register')
    

    return redirect('/')

@app.route('/login_user', methods=['POST'])
def login_user():
    
    data = {
        'email': request.form['email']
    }

    user_in_db = user.User.get_user_by_email(data)

    if not user_in_db:
        flash('Invalid email/password.', 'login')
        return redirect('/')
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        flash('Invalid email/password', 'login')
        return redirect('/')
    

    session['user_id'] = user_in_db.id
    session['first_name'] = user_in_db.first_name

    return redirect('/dashboard')


@app.route('/dashboard')
def home():

    todays_date = datetime.datetime.now().strftime("%B %d")
    todays_date2 = date.today().strftime("%Y %m %d")

    user_events = event.Event.get_user_events(session['user_id'])

    dates = []
    for x in range(len(user_events)):
        dates.append(user_events[x]['date'])

    event_notifications = 0
    for x in dates:
        if x.strftime("%Y %m %d") == todays_date2:
            event_notifications += 1
      

    amount_users = []
    for x in range(len(user_events)):
        amount_users.append(event.Event.get_members_joined(user_events[x]['id']))



    for x in range(len(user_events)):
        user_events[x]['joiners'] = amount_users[x]['ActiveMembers']
    

    return render_template('home_page.html', todays_date=todays_date, user_events=user_events, event_notifications=event_notifications)


@app.route('/create_event')
def create():
    return render_template("new_event.html")


@app.route('/add_new_event', methods=['POST'])
def add_new_event():
    
    event.Event.add_event(request.form) 

    return redirect('/dashboard')


@app.route('/search')
def search():

    all_events = event.Event.get_all_events()
    
    the_user_id = []
    for x in range(len(all_events)):
        the_user_id.append(all_events[x].user_id)

    creators = user.User.get_creators_of_events(tuple(the_user_id))


    amount_users = []
    for x in range(len(all_events)):
        amount_users.append(event.Event.get_members_joined(all_events[x].id))


    for x in range(len(all_events)):
        setattr(all_events[x], 'creator', f"{creators[x]['first_name']} {creators[x]['last_name']}")
        setattr(all_events[x], 'active_members', amount_users[x]['ActiveMembers']) 

    users_joined = event.Event.get_all_users_in_events()

    user_ids_joined = []
    sporting_ids = []
    for x in range(len(users_joined)):
        user_ids_joined.append(users_joined[x]['user_id'])
        sporting_ids.append(users_joined[x]['sporting_event_id'])


    return render_template('search.html', all_events=all_events, joiners=user_ids_joined, sports=sporting_ids)


@app.route('/add_member_to_event/<int:user_id>/<int:sporting_event_id>')
def add_member(user_id, sporting_event_id):
    data = {
        'sporting_event_id': sporting_event_id,
        'user_id': user_id
    }

    event.Event.add_member_to_event(data)

    return redirect('/search')


@app.route('/event/<int:event_id>')
def event_info(event_id):

    data = {
        'id': event_id
    }

    selected_event = event.Event.get_searched_event(data)
    event_messages = event.Event.select_event_messages(data)

    if len(event_messages) > 0:
        user_msg = user.User.get_user_by_id(event_messages[0]['user_id'])
        name = f"{user_msg[0]['first_name']} {user_msg[0]['last_name']}"
    else:
        name = None


    event_date = str(selected_event[0]['date'])
    date = datetime.datetime.strptime(event_date, "%Y-%m-%d %H:%M:%S")
    new_date = str(date)
    month = new_date[5:7]
    day = new_date[8:10]
    year = new_date[0:4]
    time1 = int(new_date[11:13])
    time2 = new_date[13:16]
    final_date = f"{month}/{day}"
    

    date_for_ui = f"{month}-{day}-{year}"

    if time1 > 12:
        time_for_ui = f"{time1 - 12}{time2} pm"
    else:
        time_for_ui = f"{time1}{time2} am"

    
    url = f"https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/selected/{final_date}"
    r = requests.get(url)
    new_data = r.json()
    
    info = []
    for dic in new_data['selected']:
        for key,val in dic.items():
            if key == 'text':
                info.append(val)
    
    
    return render_template('select_search_page.html', info=info, event=selected_event, date=date_for_ui, time=time_for_ui, messages=event_messages, name=name)


@app.route('/add_message_to_event/<int:sporting_event_id>/<int:user_id>')
def create_message(sporting_event_id, user_id):
    return render_template('new_message.html', sporting_event_id=sporting_event_id, user_id=user_id)


@app.route('/new_message', methods=['POST'])
def add_message():
    event.Event.add_new_message(request.form)
    return redirect(f"/event/{request.form['sporting_event_id']}")


@app.route('/account_page')
def account():
    the_user = user.User.get_user_by_first_name(session['first_name'])
    user_events = event.Event.get_user_events(session['user_id'])
    

    today = date.today()
    new = today.strftime("%Y-%m-%d")
    new_today = time.strptime(new, '%Y-%m-%d')

    upcoming = []
    historical = []
    for x in range(len(user_events)):
        the_date = user_events[x]['date'].strftime("%Y-%m-%d")
        new_date = time.strptime(the_date, '%Y-%m-%d')
        if new_today > new_date:
            historical.append(user_events[x]['name'])
        else:
            upcoming.append(user_events[x]['name'])
        
    print(upcoming)
        

    
    return render_template('account_page.html', the_user=the_user, events=user_events, old=historical, new=upcoming)

    

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')