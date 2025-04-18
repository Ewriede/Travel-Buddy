from datetime import datetime, timezone
from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, \
    EmptyForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Travelplan, Destination, Activities, ActivityToPlan


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/travel_packages')
def travel_packages():
    travel_plans = Travelplan.query.all()
    return render_template('travel_packages.html', title='Travel Packages', travel_plans=travel_plans)

@app.route('/pack/<plan>')
def pack(plan):
    try:
        plan_id = int(plan)
    except ValueError:
        return "Invalid unit ID format", 400

    travel_pack = ActivityToPlan.query.filter_by(plan_id=plan_id).all()

    return render_template('pack.html', title='Travel_Pack', travel_pack=travel_pack)

@app.route("/populate_db")
def populate_db():
    reset_db()
    user_1 = User(username="Billy", password_hash="", about_me="cool_person_#1")
    user_1.set_password("Billy123")
    user_2 = User(username="Joe", password_hash="", about_me="cool_person_#3")
    user_2.set_password("Joe123")
    user_3 = User(username="Ethan", password_hash="", about_me="cool_person_#5")
    user_3.set_password("Ethan123")
    user_4 = User(username="Marley", password_hash="", about_me="cool_person_#7")
    user_4.set_password("Marley123")
    db.session.add_all([user_1, user_2, user_3, user_4])
    db.session.commit()

    destination_1 = Destination(name="USA")
    destination_2 = Destination(name="Japan")
    destination_3 = Destination(name="Canada")
    db.session.add_all([destination_1, destination_2, destination_3])
    db.session.commit()

    plan_1 = Travelplan(name="Swim School", time_needed="2 Weeks", budget="1000", group_rec="4", owner=user_1, destination_plan=destination_1)
    plan_2 = Travelplan(name="Shopping Spree", time_needed="3 Days", budget="250", group_rec="3", owner=user_2, destination_plan=destination_2)
    plan_3 = Travelplan(name="From a Walk to a Ride", time_needed="1 Month", budget="5000", group_rec="6", owner=user_3, destination_plan=destination_3)
    plan_4 = Travelplan(name="Skipping School", time_needed="2 Days", budget="150", group_rec="2", owner=user_2, destination_plan=destination_1)
    db.session.add_all([plan_1, plan_2, plan_3, plan_4])
    db.session.commit()

    activity_1 = Activities(name="swim", establishment="pool.exe", description="Cool Pool", destination_activity=destination_1)
    activity_2 = Activities(name="walk", establishment="trail.exe", description="Cool Trail", destination_activity=destination_3)
    activity_3 = Activities(name="shop", establishment="shop.exe", description="Cool Shop", destination_activity=destination_2)
    activity_4 = Activities(name="school", establishment="school.exe", description="Why?", destination_activity=destination_1)
    activity_5 = Activities(name="sled", establishment="sled.exe", description="Cool Sled", destination_activity=destination_3)
    activity_6 = Activities(name="Roller Coaster", establishment="Coaster.exe", description="Cool Coaster", destination_activity=destination_1)
    db.session.add_all([activity_1, activity_2, activity_3, activity_4, activity_5, activity_6])
    db.session.commit()

    join_1 = ActivityToPlan(plan=plan_1, active=activity_1)
    join_2 = ActivityToPlan(plan=plan_1, active=activity_4)
    join_3 = ActivityToPlan(plan=plan_2, active=activity_3)
    join_5 = ActivityToPlan(plan=plan_3, active=activity_2)
    join_6 = ActivityToPlan(plan=plan_3, active=activity_5)
    join_7 = ActivityToPlan(plan=plan_4, active=activity_4)
    join_8 = ActivityToPlan(plan=plan_4, active=activity_6)
    db.session.add_all([join_1, join_2, join_3, join_5, join_6, join_7, join_8])
    db.session.commit()


    flash("Database has been populated")
    return render_template('index.html', title='populate')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = RegistrationForm()

    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            password="",
            about_me=form.about_me.data
        )
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()
        flash(f'User {form.username.data} has been added!', 'success')
        return redirect(url_for('index'))

    return render_template('register.html', title='Add User', form=form)

@app.route('/reset_db')
def reset_db():
   flash("Resetting database: deleting old data and repopulating with dummy data")
   # clear all data from all tables
   meta = db.metadata
   for table in reversed(meta.sorted_tables):
       print('Clear table {}'.format(table))
       db.session.execute(table.delete())
   db.session.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=True)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))