# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User, Post
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from flask import request
from urllib.parse import urlparse 
from datetime import datetime


@app.route('/')
@app.route('/index')
@login_required
def index():
    following_posts = User.followed_posts(self=current_user)
    return render_template('index.html', title='Home', posts=following_posts, user=current_user)

@app.route('/user/<login>')
@login_required
def user(login):
    user = User.query.filter_by(login=login).first_or_404()
    posts = Post.query.filter_by(user_id=current_user.id).all()
    return render_template('user.html', user=user, posts=posts)
    
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user is None or not user.check_password(form.password.data):
            #flash('Invalid login or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name = form.name.data, surname = form.surname.data, login=form.login.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        #flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('registration.html', title='Registration', form=form)

@app.route('/follow/<login>')
@login_required
def follow(login): 
    user = User.query.filter_by(login=login).first()
    if user is None:
        #flash('User {} not found.'.format(login))
        return redirect(url_for('index'))
    if user == current_user:
        #flash('You cannot follow yourself!')
        return redirect(url_for('user', login=login))
    current_user.follow(user)
    db.session.commit()
    #flash('You are following {}!'.format(login))
    return redirect(url_for('user', login=login))

@app.route('/unfollow/<login>')
@login_required
def unfollow(login):
    user = User.query.filter_by(login=login).first()
    if user is None:
        #flash('User {} not found.'.format(login))
        return redirect(url_for('index'))
    if user == current_user:
        #flash('You cannot unfollow yourself!')
        return redirect(url_for('user', login=login))
    current_user.unfollow(user)
    db.session.commit()
    #flash('You are not following {}.'.format(login))
    return redirect(url_for('user', login=login))

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.login)
    if form.validate_on_submit():
        current_user.login = form.login.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        #flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.login.data = current_user.login
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

