from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import requests
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- DATABASE MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_blocked = db.Column(db.Boolean, default=False)
    block_reason = db.Column(db.String(500), default="")
    # User ke saare websites yahan link honge
    websites = db.relationship('Website', backref='user', lazy=True)

class Website(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Checking...")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- MONITOR ENGINE ---
def monitor_background_task():
    while True:
        with app.app_context():
            sites = Website.query.all()
            for site in sites:
                try:
                    requests.get(site.url, timeout=10)
                    site.status = "Active ✅"
                except:
                    site.status = "Dead ❌"
            db.session.commit()
        time.sleep(60)

threading.Thread(target=monitor_background_task, daemon=True).start()

# --- ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Admin Login Check (Direct)
        if email == 'admin@admin.com' and password == 'admin123':
             # Admin ke liye fake user object
            admin_user = User.query.filter_by(email='admin@admin.com').first()
            if not admin_user:
                admin_user = User(email='admin@admin.com', password='admin123')
                db.session.add(admin_user)
                db.session.commit()
            login_user(admin_user)
            return redirect('/admin')

        user = User.query.filter_by(email=email).first()
        if user:
            if user.is_blocked:
                return render_template('login.html', error=f"⛔ BLOCKED: {user.block_reason}")
            if user.password == password:
                login_user(user)
                return redirect('/dashboard')
        
        return render_template('login.html', error="Wrong Email or Password")
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email')
    password = request.form.get('password')
    if User.query.filter_by(email=email).first():
        return "Email already exists"
    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return redirect('/')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.email == 'admin@admin.com':
        return redirect('/admin')
        
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            new_site = Website(url=url, user_id=current_user.id)
            db.session.add(new_site)
            db.session.commit()
    
    user_sites = Website.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', sites=user_sites)

# --- NEW ADMIN PANEL LOGIC ---
@app.route('/admin')
@login_required
def admin():
    if current_user.email != 'admin@admin.com':
        return "Access Denied"
    
    users = User.query.all()
    all_sites = Website.query.all()
    
    # Stats Calculation
    stats = {
        'total_users': len(users),
        'active_monitors': len(all_sites),
        'downloads': 150 + len(users) * 2 # Fake logic to show downloads
    }
    
    return render_template('admin.html', users=users, stats=stats)

@app.route('/block_user/<int:id>', methods=['POST'])
@login_required
def block_user(id):
    if current_user.email != 'admin@admin.com': return "Denied"
    user = User.query.get(id)
    user.is_blocked = True
    user.block_reason = request.form.get('reason')
    db.session.commit()
    return redirect('/admin')

@app.route('/delete_user/<int:id>')
@login_required
def delete_user(id):
    if current_user.email != 'admin@admin.com': return "Denied"
    user = User.query.get(id)
    # Pehle user ke websites delete karo
    Website.query.filter_by(user_id=id).delete()
    db.session.delete(user)
    db.session.commit()
    return redirect('/admin')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
