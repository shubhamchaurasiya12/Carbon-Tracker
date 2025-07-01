from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import csv
import io
import json
import random
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carbon_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # type: ignore

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')
    carbon_limit = db.Column(db.Float, nullable=True)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    emissions = db.relationship('Emission', backref='user', lazy=True)

class Emission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    activity_type = db.Column(db.String(50), nullable=False)
    emission_kgco2e = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(20), default='manual')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_panel'))
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin_panel'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        carbon_limit = request.form.get('carbon_limit')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        hashed_password = generate_password_hash(password)
        user = User()
        user.full_name = full_name
        user.email = email
        user.password = hashed_password
        user.carbon_limit = float(carbon_limit) if carbon_limit else None
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_panel'))
    
    # Get current month emissions
    current_month = date.today().replace(day=1)
    emissions = Emission.query.filter(
        Emission.user_id == current_user.id,
        Emission.date >= current_month
    ).all()
    
    # Calculate totals
    total_emissions = sum(e.emission_kgco2e for e in emissions)
    
    # Group by category
    category_breakdown = {}
    for emission in emissions:
        if emission.activity_type not in category_breakdown:
            category_breakdown[emission.activity_type] = 0
        category_breakdown[emission.activity_type] += emission.emission_kgco2e
    
    # Get daily emissions for chart
    daily_emissions = {}
    for emission in emissions:
        day = emission.date.strftime('%Y-%m-%d')
        if day not in daily_emissions:
            daily_emissions[day] = 0
        daily_emissions[day] += emission.emission_kgco2e
    
    # Check if limit exceeded
    limit_exceeded = False
    if current_user.carbon_limit and total_emissions > current_user.carbon_limit:
        limit_exceeded = True
    
    return render_template('dashboard.html',
                         total_emissions=total_emissions,
                         category_breakdown=category_breakdown,
                         daily_emissions=daily_emissions,
                         limit_exceeded=limit_exceeded,
                         now=datetime.now())

@app.route('/update_limit', methods=['POST'])
@login_required
def update_limit():
    if current_user.role == 'admin':
        return redirect(url_for('admin_panel'))
    
    new_limit = request.form.get('carbon_limit')
    if new_limit:
        current_user.carbon_limit = float(new_limit)
        db.session.commit()
        flash('Carbon limit updated successfully!', 'success')
    
    return redirect(url_for('dashboard'))

@app.route('/add_emission', methods=['POST'])
@login_required
def add_emission():
    if current_user.role == 'admin':
        return redirect(url_for('admin_panel'))
    
    activity_type = request.form['activity_type']
    emission_kgco2e = float(request.form['emission_kgco2e'])
    
    # Check if entry exists for today
    today = date.today()
    existing_entry = Emission.query.filter_by(
        user_id=current_user.id,
        date=today,
        activity_type=activity_type
    ).first()
    
    if existing_entry:
        existing_entry.emission_kgco2e = emission_kgco2e
        flash('Today\'s entry updated successfully!', 'success')
    else:
        new_emission = Emission(
            user_id=current_user.id,
            activity_type=activity_type,
            emission_kgco2e=emission_kgco2e
        )
        db.session.add(new_emission)
        flash('Emission entry added successfully!', 'success')
    
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    users = User.query.all()
    emissions = Emission.query.all()
    
    # Get mock IoT data count
    mock_data_count = Emission.query.filter_by(source='mock_iot').count()
    
    return render_template('admin.html', users=users, emissions=emissions, mock_data_count=mock_data_count)

@app.route('/admin/upload_csv', methods=['POST'])
@login_required
@admin_required
def upload_csv():
    if 'csv_file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('admin_panel'))
    
    file = request.files['csv_file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('admin_panel'))
    
    try:
        # Read CSV
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        count = 0
        for row in csv_reader:
            user = User.query.filter_by(email=row['email']).first()
            if user:
                emission = Emission(
                    user_id=user.id,
                    date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                    activity_type=row['activity_type'],
                    emission_kgco2e=float(row['emission_kgco2e']),
                    source=row.get('source', 'mock_iot')
                )
                db.session.add(emission)
                count += 1
        
        db.session.commit()
        flash(f'Successfully uploaded {count} emission records', 'success')
        
    except Exception as e:
        flash(f'Error processing CSV: {str(e)}', 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/add_mock_data', methods=['POST'])
@login_required
@admin_required
def add_mock_data():
    user_id = request.form.get('user_id')
    activity_type = request.form.get('activity_type')
    emission_kgco2e_str = request.form.get('emission_kgco2e')
    
    if not emission_kgco2e_str:
        flash('Emission value is required', 'error')
        return redirect(url_for('admin_panel'))
    
    emission_kgco2e = float(emission_kgco2e_str)
    
    emission = Emission(
        user_id=user_id,
        activity_type=activity_type,
        emission_kgco2e=emission_kgco2e,
        source='mock_iot'
    )
    
    db.session.add(emission)
    db.session.commit()
    
    flash('Mock data added successfully!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/api/dashboard_data')
@login_required
def dashboard_data():
    if current_user.role == 'admin':
        return jsonify({'error': 'Admin access denied'})
    
    # Get current month emissions
    current_month = date.today().replace(day=1)
    emissions = Emission.query.filter(
        Emission.user_id == current_user.id,
        Emission.date >= current_month
    ).all()
    
    # Calculate totals
    total_emissions = sum(e.emission_kgco2e for e in emissions)
    
    # Group by category
    category_breakdown = {}
    for emission in emissions:
        if emission.activity_type not in category_breakdown:
            category_breakdown[emission.activity_type] = 0
        category_breakdown[emission.activity_type] += emission.emission_kgco2e
    
    # Get daily emissions for chart
    daily_emissions = {}
    for emission in emissions:
        day = emission.date.strftime('%Y-%m-%d')
        if day not in daily_emissions:
            daily_emissions[day] = 0
        daily_emissions[day] += emission.emission_kgco2e
    
    return jsonify({
        'total_emissions': total_emissions,
        'category_breakdown': category_breakdown,
        'daily_emissions': daily_emissions,
        'carbon_limit': current_user.carbon_limit,
        'limit_exceeded': current_user.carbon_limit and total_emissions > current_user.carbon_limit
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@carbon.com').first()
        if not admin:
            admin = User()
            admin.full_name = 'Admin User'
            admin.email = 'admin@carbon.com'
            admin.password = generate_password_hash('admin123')
            admin.role = 'admin'
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: admin@carbon.com / admin123")
    
    app.run(debug=True) 