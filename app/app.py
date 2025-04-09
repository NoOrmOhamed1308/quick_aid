from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid
import treepoem  # Changed from segno to treepoem
from datetime import datetime
from PIL import Image, ImageChops


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quick_aid.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models (unchanged functionality)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    details = db.relationship('Details', backref='user', lazy=True)

class Details(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(36), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    emergency_contact = db.Column(db.String(15), nullable=False)
    vehicle_number = db.Column(db.String(20), unique=True, nullable=False)
    blood_group = db.Column(db.String(50))
    allergies = db.Column(db.String(255))
    differently_abled = db.Column(db.String(255))
    alternate_contact = db.Column(db.String(15))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Utility Functions (updated implementation but same functionality)
def generate_uid():
    return str(uuid.uuid4())

def generate_aztec_code(uid):
    """Generate Aztec code pointing to details page"""
    output_folder = os.path.join('static', 'aztec_codes')
    os.makedirs(output_folder, exist_ok=True)

    filename = f"{uid}_aztec.png"
    filepath = os.path.join(output_folder, filename)

    try:
        # Replace this with your real site domain when deployed
        site_url = "https://quick-aid.onrender.com"
        full_url = f"{site_url}/details/{uid}"

        image = treepoem.generate_barcode(
            barcode_type='azteccode',
            data=full_url
        ).convert('L')

        # Trim white space
        bg = Image.new(image.mode, image.size, 255)
        diff = ImageChops.difference(image, bg)
        bbox = diff.getbbox()
        if bbox:
            image = image.crop(bbox)

        # Save the final image
        image.save(filepath)
        return filepath
    except Exception as e:
        print(f"Error generating barcode: {e}")
        return None

# Routes (all routes remain exactly the same)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials!', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    details = Details.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', details=details)

@app.route('/add_details', methods=['GET', 'POST'])
@login_required
def add_details():
    if request.method == 'POST':
        try:
            uid = generate_uid()
            aztec_path = generate_aztec_code(uid)
            
            if not aztec_path:
                raise Exception("Failed to generate Aztec code")

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
            flash('Details added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('add_details'))

    return render_template('add_details.html')

@app.route('/edit_details/<uid>', methods=['GET', 'POST'])
@login_required
def edit_details(uid):
    detail = Details.query.filter_by(uid=uid, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        detail.name = request.form['name']
        detail.emergency_contact = request.form['emergency_contact']
        detail.vehicle_number = request.form['vehicle_number']
        detail.blood_group = request.form.get('blood_group')
        detail.allergies = request.form.get('allergies')
        detail.differently_abled = request.form.get('differently_abled')
        detail.alternate_contact = request.form.get('alternate_contact')
        db.session.commit()
        flash('Details updated!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_details.html', detail=detail)

@app.route('/details/<uid>')
def show_details(uid):
    detail = Details.query.filter_by(uid=uid).first_or_404()
    return render_template('show_details.html', detail=detail)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out!', 'info')
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)