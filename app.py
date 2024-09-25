from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Set up logging
logging.basicConfig(filename='app.log', level=logging.WARNING)

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User,{"id": user_id})

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            login_user(user)
            logging.info(f"User {username} logged in.")
            return redirect(url_for('profile'))
        else:
            flash('Login Failed. Check your username and password.', 'danger')
            logging.warning(f"Failed login attempt for {username}.")
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logging.info(f"User {current_user.username} logged out.")
    logout_user()
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    logging.error(f'404 Error: {request.path} not found')
    return render_template('404.html'), 404


@app.route('/profile')
@login_required
def profile():
    logging.info(f"Profile page accessed by {current_user.username}.")
    return render_template('profile.html', username=current_user.username)

if __name__ == "__main__":
    app.run(debug=True,port="5000",host="0.0.0.0")
