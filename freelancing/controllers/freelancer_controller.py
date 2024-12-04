from flask import Blueprint, jsonify, request
from freelancing import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from freelancing.models.admins import Admin
from freelancing.models.jobposter import JobPoster
from freelancing.models.freelancer import Freelancer
from freelancing.models.project import Project
from freelancing.models.payment import Payment
from freelancing.models.contract import Contract
from flask import session, redirect, url_for, render_template
# Create a Blueprint for Freelancer
from freelancing import freelancing
from freelancing.models.application import Application
from bson import ObjectId
from datetime import datetime




@freelancing.route('/freelancer_register', methods=['GET', 'POST'])
def freelancer_register():
    """
    Freelancer registration route.
    """
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        password = data.get('password')
        username = data.get('username')
        account_details ={
            "account_number": data.get('account_number'),
            "routing_number": data.get('routing_number')
        }

        # Check if freelancer already exists
        if Freelancer.exists_by_email(email):
            return "Freelancer with this email already exists", 400

        # Hash password and create freelancer
        hashed_password = generate_password_hash(password)
        freelancer_data = {
            "email": email,
            "password": hashed_password,
            "username": username,
            "account_details": account_details,
            "status": "active"
        }
        Freelancer.create(freelancer_data)
        return redirect(url_for('login'))  # Redirect to login after successful registration

    return render_template('freelancers/register.html')



@freelancing.route('/freelancer_dashboard')
def freelancer_dashboard():
    """
    Render the Admin dashboard.
    """
    return render_template('freelancers/dashboard.html')





@freelancing.route('/freelancer_projects')
def freelancer_projects():
    """
    Display available projects for freelancers.
    """
    if session.get("user_type") != "freelancer":
        return redirect(url_for('login'))

    freelancer_id = session.get("user_id")

    # Fetch open projects from MongoDB
    projects = list(Project.find({"status": "open"}))

    # Check if the freelancer has applied for each project
    for project in projects:
        application = Application.find_one({
            "project_id": project["_id"],
            "freelancer_id": ObjectId(freelancer_id)
        })
        project["applied"] = bool(application)  # Add applied status
        if application:
            project["application_id"] = str(application["_id"])  # Add application ID for "View Application"

    return render_template('freelancers/projects.html', projects=projects)





@freelancing.route('/freelancer_contracts')
def freelancer_contracts():
    """
    Display active and pending contracts for freelancers.
    """
    if session.get("user_type") != "freelancer":
        return redirect(url_for('login'))

    freelancer_id = session.get("user_id")

    # Fetch accepted contracts
    accepted_contracts = list(
        Contract.find({"freelancer_id": ObjectId(freelancer_id), "status": "accepted"})
    )

    # Fetch pending contracts
    pending_contracts = list(
        Contract.find({"freelancer_id": ObjectId(freelancer_id), "status": "pending"})
    )

    # Add job poster details to contracts
    for contract in accepted_contracts + pending_contracts:
        jobposter = JobPoster.find_one({"_id": contract["jobposter_id"]})
        contract["jobposter_name"] = jobposter.get("username", "N/A")
        contract["jobposter_company"] = jobposter.get("company", "N/A")

    return render_template(
        'freelancers/contracts.html',
        accepted_contracts=accepted_contracts,
        pending_contracts=pending_contracts
    )


@freelancing.route('/apply_project/<project_id>', methods=['GET', 'POST'])
def apply_project(project_id):
    """
    Apply for a project and add an initial comment.
    """
    if session.get("user_type") != "freelancer":
        return redirect(url_for('login'))

    if request.method == 'POST':
        freelancer_id = session.get("user_id")
        proposed_budget = float(request.form.get('proposed_budget'))
        skills = request.form.get('skills')
        proposal = request.form.get('proposal')
        initial_comment = request.form.get('comment')

        application_data = {
            "freelancer_id": ObjectId(freelancer_id),
            "project_id": ObjectId(project_id),
            "proposed_budget": proposed_budget,
            "skills": skills,
            "proposal": proposal,
            "comments": [  # Initialize as an array
                {
                    "user_type": "freelancer",
                    "message": initial_comment,
                    "timestamp": datetime.now()
                }
            ],
        }

        Application.insert_one(application_data)
        return redirect(url_for('freelancer_projects'))

    project = Project.find_one({"_id": ObjectId(project_id)})
    return render_template('freelancers/apply_project.html', project=project)


@freelancing.route('/view_application/<application_id>', methods=['GET', 'POST'])
def view_application(application_id):
    """
    View an existing application and handle the chat feature (comments) between freelancer and job poster.
    """
    if session.get("user_type") != "freelancer" and session.get("user_type") != "jobposter":
        return redirect(url_for('login'))

    # Fetch the application details
    application = Application.find_one({"_id": ObjectId(application_id)})
    if not application:
        return "Application not found", 404

    # Fetch the associated project details
    project = Project.find_one({"_id": application["project_id"]})

    if request.method == "POST":
        # Handle adding a new comment
        new_comment = {
            "user_type": session.get("user_type"),
            "message": request.form.get("message"),
            "timestamp": datetime.now()
        }
        Application.append_comment(application_id, new_comment)

    # Fetch updated application details
    application = Application.find_one({"_id": ObjectId(application_id)})

    return render_template(
        "freelancers/view_application.html",
        application=application,
        project=project
    )


@freelancing.route('/add_comment/<project_id>', methods=['POST'])
def add_comment(project_id):
    """
    Add a comment to a project.
    """
    if session.get("user_type") != "freelancer":
        return redirect(url_for('login'))

    freelancer_id = session.get("user_id")
    message = request.form.get('message')

    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400

    comment = {
        "freelancer_id": ObjectId(freelancer_id),
        "message": message,
        "timestamp": datetime.now(),
    }

    Project.collection.update_one(
        {"_id": ObjectId(project_id)},
        {"$push": {"comments": comment}}
    )
    return redirect(url_for('view_project_comments', project_id=project_id))



@freelancing.route('/view_project_comments/<project_id>', methods=['GET'])
def view_project_comments(project_id):
    """
    View all comments for a specific project.
    """
    if session.get("user_type") != "jobposter":
        return redirect(url_for('login'))

    project = Project.find_one({"_id": ObjectId(project_id)})
    if not project:
        return "Project not found", 404

    comments = project.get("comments", [])
    return render_template('jobposters/comments.html', comments=comments, project=project)
