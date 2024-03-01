from flask import Flask, render_template, request, redirect, url_for, flash,jsonify, session
from werkzeug.security import check_password_hash
from flask_login import login_user
from models import User, Feedback,Answer,db  # Adjust the import according to your project structure
from flask import Blueprint
from flask_login import current_user,LoginManager, logout_user, login_required
from werkzeug.security import generate_password_hash
import os
import pandas as pd
from functools import wraps
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = 'NOTHINGISLIKEOURSECRETKEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session or session['admin'] != True:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

with app.app_context():
    db.create_all()

@app.route('/register')
def register():
    print('register')
    script_directory = os.path.dirname(os.path.abspath(__file__))

    os.chdir(script_directory)

    df = pd.read_excel('users.xlsx', engine='openpyxl') 
# Loop through each row in the DataFrame and register users
    for index, row in df.iterrows():
        print(row)
        email = row['Email']
        email = email.lower()  # Ensure email is lowercase
        password = row['CNIC']  # Assuming CNIC column exists and is used as the password
        hashed_password = str(password)
        user_type = 'participant'

        # Create a User instance (make sure to integrate with your database session)
        user = User(email=email, password_hash=hashed_password, user_type=user_type)
        db.session.add(user)
        db.session.commit()
    
    
    return 'Users registered successfully!'
    


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    # Access form data using request.form['input_name']
    feedback_type = request.form.get('feedback_type')
    challenge = request.form.get('challenge')  # This will be None if not set
    feedback_description = request.form.get('feedback_description')

    # You would then typically save this data to your database
    new_feedback = Feedback(feedback_type=feedback_type, challenge_name=challenge, description=feedback_description, user_id=current_user.id)
    db.session.add(new_feedback)
    db.session.commit()

    # Redirect or respond as necessary
    return redirect(url_for('mainpage'))

@login_required
@app.route('/mainpage')
def mainpage():
    all_feedbacks = Feedback.query.all()  # Or apply some filtering/ordering as needed
    all_answers = Answer.query.all()
    return render_template('mainpage.html', feedbacks=all_feedbacks,answers=all_answers)

@login_required
@app.route('/feedback')
def feedback():
    # Get the directory of the current script
    script_directory = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the script directory
    os.chdir(script_directory)
    with open('challenges.txt', 'r') as file:
        challenges = [line.strip() for line in file]
    user = current_user
    return render_template('feedback.html',user=user, challenges=challenges)
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    if 'admin' in session and session['admin'] == True:
        feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()

        return render_template('admin.html', feedbacks=feedbacks)
    

@login_required
@app.route('/submit-answer/<int:feedback_id>', methods=['POST'])
def submit_answer(feedback_id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    answer_content = request.form.get('answer_content')
    new_answer = Answer(content=answer_content, feedback_id=feedback_id)  # Relate the new answer to the feedback
    db.session.add(new_answer)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        print(user)
        print(user.password_hash)
        # Check if user actually exists and the password is correct
        # check_password_hash(user.password_hash, password)
        if not user or not user.password_hash == password:
            flash('Please check your login details and try again.')
            return jsonify({'error': 'Invalid credentials'}), 401  # Unauthorized

        # If the above check passes, then we know the user has the right credentials
        login_user(user)
        session['admin'] = user.user_type == 'admin'
        if user.user_type == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('mainpage'))  # Redirect to the profile page, for example

    return render_template('login.html')  # Render the login template if GET


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
