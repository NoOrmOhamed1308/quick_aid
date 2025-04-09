from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from app import app, db
from app.models import User, Details
from werkzeug.security import generate_password_hash, check_password_hash
import segno
import os
import random
import string

# Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        # ✅ Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        # ✅ Hash password and store new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
            print(f"Error during registration: {e}")

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    details = Details.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', details=details)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/add_details', methods=['GET', 'POST'])
@login_required
def add_details():
    if request.method == 'POST':
        try:
            uid = generate_uid()
            details = Details(
                uid=uid,
                name=request.form['name'],
                emergency_contact=request.form['emergency_contact'],
                vehicle_number=request.form['vehicle_number'],
                blood_group=request.form.get('blood_group'),
                allergies=request.form.get('allergies'),
                differently_abled=request.form.get('differently_abled'),
                alternate_contact=request.form.get('alternate_contact'),
                user_id=current_user.id
            )
            db.session.add(details)
            db.session.commit()

            # Generate Aztec code
            aztec_code_path = generate_aztec_code(uid)
            details.aztec_code_path = aztec_code_path
            db.session.commit()

            flash('Details added successfully! Aztec code generated.', 'success')
            return redirect(url_for('dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding details: {e}', 'danger')
            return redirect(url_for('add_details'))

    return render_template('add_details.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))