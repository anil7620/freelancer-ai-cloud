from flask import Blueprint, jsonify, request
from freelancing import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from freelancing.models.admins import Admin
from freelancing.models.jobposter import JobPoster
from freelancing.models.payment import Payment
from freelancing.models.project import Project
from freelancing.models.freelancer import Freelancer
from flask import session, redirect, url_for, render_template
from freelancing import freelancing



@freelancing.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    """
    Admin registration `route`.
    """
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        password = data.get('password')

        # Check if admin already exists
        if Admin.exists_by_email(email):
            return "Admin with this email already exists", 400

        # Hash password and create admin
        hashed_password = generate_password_hash(password)
        admin_data = {"email": email, "password": hashed_password}
        Admin.create(admin_data)
        return redirect(url_for('login'))  # Redirect to login after successful registration

    return render_template('admins/register.html')



@freelancing.route('/admin_dashboard')
def admin_dashboard():
    """
    Render the Admin dashboard with dynamic data.
    """
    if session.get("user_type") != "admin":
        return redirect(url_for('login'))

    # Fetch dynamic data from MongoDB
    active_users = Freelancer.count_documents({}) + JobPoster.count_documents({})
    active_projects = Project.count_documents({"status": {"$in": ["active", "open"]}})
    
    # Sum total payments
    total_payments = Payment.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ])
    total_payments_amount = next(total_payments, {}).get("total", 0)

    # Calculate total admin commission
    total_commission = Payment.aggregate([
        {"$group": {"_id": None, "total_commission": {"$sum": "$admin_commission"}}}
    ])
    total_commission_amount = next(total_commission, {}).get("total_commission", 0)

    # Count pending users
    pending_users_count = (
        Freelancer.count_documents({"status": "pending"}) +
        JobPoster.count_documents({"status": "pending"})
    )

    # Count payment disputes
    disputes_count = Payment.count_documents({"status": "disputed"})

    return render_template(
        'admins/dashboard.html',
        active_users=active_users,
        active_projects=active_projects,
        total_payments=f"${total_payments_amount:,.2f}",
        total_commission=f"${total_commission_amount:,.2f}",
        pending_users_count=pending_users_count,
        disputes_count=disputes_count
    )

@freelancing.route('/admin_manage_freelancers')
def manage_freelancers():
    """
    View and manage freelancers.
    """
    if session.get("user_type") != "admin":
        return redirect(url_for('login'))

    freelancers = list(Freelancer.find({}))
    return render_template('admins/manage_freelancers.html', freelancers=freelancers)


@freelancing.route('/admin_manage_jobposters')
def manage_jobposters():
    """
    View and manage job posters.
    """
    if session.get("user_type") != "admin":
        return redirect(url_for('login'))

    jobposters = list(JobPoster.find({}))
    return render_template('admins/manage_jobposters.html', jobposters=jobposters)



@freelancing.route('/admin_payments')
def manage_payments():
    """
    View and manage payments.
    """
    if session.get("user_type") != "admin":
        return redirect(url_for('login'))

    payments = list(Payment.find({}))
    return render_template('admins/manage_payments.html', payments=payments)



@freelancing.route('/admin_users_pending')
def approve_pending_users():
    """
    Approve pending user accounts (freelancers and job posters).
    """
    if session.get("user_type") != "admin":
        return redirect(url_for('login'))

    pending_freelancers = list(Freelancer.find({"status": "pending"}))
    pending_jobposters = list(JobPoster.find({"status": "pending"}))

    return render_template(
        'admins/approve_users.html',
        pending_freelancers=pending_freelancers,
        pending_jobposters=pending_jobposters
    )


@freelancing.route('/admin_payments_disputes')
def resolve_disputes():
    """
    View and resolve payment disputes.
    """
    if session.get("user_type") != "admin":
        return redirect(url_for('login'))

    disputes = list(Payment.find({"status": "disputed"}))
    return render_template('admins/resolve_disputes.html', disputes=disputes)
