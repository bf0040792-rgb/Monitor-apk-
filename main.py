from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- DATABASE (User Data) ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_blocked = db.Column(db.Boolean, default=False) # Block hai ya nahi
    block_reason = db.Column(db.String(500), default="") # Admin ka message

# Database Banao
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # 1. Check User Exist
        user = User.query.filter_by(email=email).first()
        
        if user:
            # 2. Check BLOCK Status (Ye main feature hai)
            if user.is_blocked:
                # User ko Admin ka likha hua message dikhao
                return f"<h2 style='color:red; text-align:center; margin-top:50px;'>⛔ BLOCKED</h2><p style='text-align:center;'>Reason: <b>{user.block_reason}</b></p>"
            
            # 3. Check Password & Login
            if user.password == password:
                login_user(user)
                return "<h1>Login Successful! (Yahan Dashboard Hoga)</h1>"
            
        return "Wrong Email or Password"
        
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email')
    password = request.form.get('password')
    # Naya user banao
    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return "Account Created! Go back and Login."

# --- ADMIN PANEL ROUTES ---

@app.route('/admin')
def admin():
    # Saare users ki list admin ko dikhao
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/block_user/<int:id>', methods=['POST'])
def block_user(id):
    user = User.query.get(id)
    reason = request.form.get('reason') # Admin ka likha comment uthao
    
    user.is_blocked = True
    user.block_reason = reason # Database me save karo
    db.session.commit()
    return redirect('/admin')

@app.route('/delete_user/<int:id>')
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/admin')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
