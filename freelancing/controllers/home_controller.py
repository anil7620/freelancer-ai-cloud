from flask import Blueprint, jsonify, request, render_template
from freelancing import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from freelancing.models.admins import Admin
from freelancing.models.jobposter import JobPoster
from freelancing.models.freelancer import Freelancer
from flask import session, redirect, url_for
from freelancing import freelancing

# Create Blueprint for Admin




@freelancing.route('/')
def index():
    """
    Render the home page.
    """
    return render_template('index.html')



@freelancing.route('/login', methods=['GET', 'POST'])
def login():
    """
    Universal login route for Admin, Freelancer, and Job Poster.
    """
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('user_type')  # Get the user type from the form

        if not user_type:
            return "User type is required", 400

        # Check based on user type
        if user_type == 'admin':
            user = Admin.find_one({"email": email})
        elif user_type == 'freelancer':
            user = Freelancer.find_one({"email": email})
        elif user_type == 'jobposter':
            user = JobPoster.find_one({"email": email})
        else:
            return "Invalid user type", 400

        if user and check_password_hash(user['password'], password):
            session["user_id"] = str(user['_id'])
            session["user_type"] = user_type

            # Redirect based on user type
            if user_type == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user_type == 'freelancer':
                return redirect(url_for('freelancer_dashboard'))
            elif user_type == 'jobposter':
                return redirect(url_for('jobposter_dashboard'))
        else:
            return f"Invalid {user_type.capitalize()} credentials", 400

    return render_template('login.html')



@freelancing.route('/logout')
def logout():
    """
    Logout route.
    """
    session.clear()
    return redirect(url_for('index'))