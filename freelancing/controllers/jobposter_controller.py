from flask import Blueprint, jsonify, request
from freelancing import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from freelancing.models.admins import Admin
from freelancing.models.jobposter import JobPoster
from freelancing.models.freelancer import Freelancer
from freelancing.models.payment import Payment
from freelancing.models.project import Project
from freelancing.models.application import Application
from flask import session, redirect, url_for, render_template
from datetime import datetime
from freelancing import freelancing
from bson.objectid import ObjectId


@freelancing.route('/jobposter_register', methods=['GET', 'POST'])
def jobposter_register():
    """
    Job Poster registration route.
    """
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        password = data.get('password')
        username = data.get('username')
        company = data.get('company')
        account_details = {
            "account_number": data.get('account_number'),
            "routing_number": data.get('routing_number'),
        }

        # Check if job poster already exists
        if JobPoster.exists_by_email(email):
            return "Job Poster with this email already exists", 400

        # Hash password and create job poster
        hashed_password = generate_password_hash(password)
        jobposter_data = {
            "email": email,
            "password": hashed_password,
            "username": username,
            "company": company,
            "status": "active",
            "account_details": account_details
        }
        JobPoster.create(jobposter_data)
        return redirect(url_for('login'))  # Redirect to login after successful registration

    return render_template('jobposters/register.html')




@freelancing.route('/jobposter_dashboard')
def jobposter_dashboard():
    """
    Render the Job Poster dashboard with dynamic application count.
    """
    if session.get("user_type") != "jobposter":
        return redirect(url_for('login'))

    jobposter_id = session.get("user_id")
    projects = list(Project.find_by_jobposter(jobposter_id))
    application_count = Application.count_by_jobposter(jobposter_id)

    return render_template(
        'jobposters/dashboard.html',
        projects=projects,
        application_count=application_count,
    )



@freelancing.route('/jobposter_create_project', methods=['GET', 'POST'])
def jobposter_create_project():
    """
    Create a new project with predefined categories.
    """
    if session.get("user_type") != "jobposter":
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = request.form
        category_name = data.get('category_name')
        title = data.get('title')
        description = data.get('description')
        expected_cost = float(data.get('expected_cost'))
        deadline = data.get('deadline')

        # Parameters with default values
        project_data = {
            "category_name": category_name,
            "title": title,
            "description": description,
            "expected_cost": expected_cost,
            "deadline": deadline,
            "finalFreelancer_id": None,  # Default empty field
            "finalCost": None,           # Default empty field
            "intialPaid": None,         # Default False
            "finalPaid": None,          # Default False
            "status": "open",            # Default status
            "created_at": datetime.now(),
            "comments": [],
            "jobposter_id": ObjectId(session.get("user_id")),
        }

        # Insert project into MongoDB
        Project.insert_one(project_data)
        return redirect(url_for('jobposter_dashboard'))  # Redirect after successful creation

    return render_template('jobposters/create_project.html')


@freelancing.route('/jobposter_view_applications/<project_id>')
def jobposter_view_applications(project_id):
    """
    View applications for a specific project.
    """
    if session.get("user_type") != "jobposter":
        return redirect(url_for('login'))

    applications = list(Application.find({"project_id": ObjectId(project_id)}))
    # print(applications)
    return render_template('jobposters/view_applications.html', applications=applications)



@freelancing.route('/jobposter_projects')
def jobposter_projects():
    """
    View active and completed projects created by the Job Poster.
    """
    if session.get("user_type") != "jobposter":
        return redirect(url_for('login'))

    jobposter_id = session.get("user_id")
    projects = list(Project.find_by_jobposter(jobposter_id))
    # print(projects)
    return render_template('jobposters/projects.html', projects=projects)


@freelancing.route('/toggle_project_status/<project_id>', methods=['POST'])
def toggle_project_status(project_id):
    """
    Toggle the status of a project between 'open' and 'closed'.
    """
    if session.get("user_type") != "jobposter":
        return redirect(url_for('login'))

    # Find the project
    project = Project.find_one({"_id": ObjectId(project_id)})
    if not project:
        return "Project not found", 404

    # Toggle the status
    new_status = "closed" if project["status"] == "open" else "open"
    Project.update(project_id, {"status": new_status})

    return redirect(url_for('jobposter_projects'))

@freelancing.route('/edit_project/<project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    """
    Edit an existing project.
    """
    if session.get("user_type") != "jobposter":
        return redirect(url_for('login'))

    # Fetch the project by ID
    project = Project.find_one({"_id": ObjectId(project_id)})

    if not project:
        return "Project not found", 404

    if request.method == 'POST':
        data = request.form
        updated_data = {
            "category_name": data.get('category_name'),
            "title": data.get('title'),
            "description": data.get('description'),
            "expected_cost": float(data.get('expected_cost')),
            "deadline": data.get('deadline'),
        }
        # Update the project
        Project.update(project_id, updated_data)
        return redirect(url_for('jobposter_projects'))

    # Render edit form with the current project data
    return render_template('jobposters/edit_project.html', project=project)


@freelancing.route('/delete_project/<project_id>', methods=['POST'])
def delete_project(project_id):
    """
    Delete an existing project.
    """
    if session.get("user_type") != "jobposter":
        return redirect(url_for('login'))

    # Delete the project
    Project.delete(project_id)
    return redirect(url_for('jobposter_projects'))




@freelancing.route('/jobposter_view_application/<application_id>', methods=['GET', 'POST'])
def jobposter_view_application(application_id):
    """
    View an existing application and handle the chat feature (comments) between job poster and freelancer.
    """
    if session.get("user_type") != "jobposter":
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
        "jobposters/view_application.html",
        application=application,
        project=project
    )
