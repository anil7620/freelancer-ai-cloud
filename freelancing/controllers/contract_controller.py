
from flask import Blueprint, jsonify, request
from freelancing import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from freelancing.models.admins import Admin
from freelancing.models.jobposter import JobPoster
from freelancing.models.contract import Contract
from freelancing.models.freelancer import Freelancer
from freelancing.models.payment import Payment
from freelancing.models.project import Project
from freelancing.models.application import Application
from flask import session, redirect, url_for, render_template
from datetime import datetime
from freelancing import freelancing
from bson.objectid import ObjectId








@freelancing.route('/start_contract/<application_id>', methods=['GET', 'POST'])
def start_contract(application_id):
    """
    Start a contract based on the selected application.
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
        # Collect contract details from the form
        final_budget = float(request.form.get("final_budget"))
        expected_date_of_completion = request.form.get("expected_date_of_completion")
        jobposter_id = session.get("user_id")

        # Create the contract
        contract_data = {
            "freelancer_id": application["freelancer_id"],
            "project_id": application["project_id"],
            "application_id": ObjectId(application_id),
            "jobposter_id": ObjectId(jobposter_id),
            "final_budget": final_budget,
            "expected_date_of_completion": expected_date_of_completion,
            "status": "pending",
            "created_at": datetime.now()
        }
        Contract.insert_one(contract_data)
        Project.update_status(application["project_id"], "closed")  # Update project status to closed

        return redirect(url_for("jobposter_projects"))  # Redirect to projects after contract creation

    return render_template(
        "jobposters/start_contract.html",
        application=application,
        project=project
    )




@freelancing.route('/accept_contract/<contract_id>', methods=['POST'])
def accept_contract(contract_id):
    """
    Accept a contract, create an initial payment, and update the project details.
    """
    if session.get("user_type") != "freelancer":
        return redirect(url_for('login'))

    # Fetch the contract details
    contract = Contract.find_one({"_id": ObjectId(contract_id)})
    if not contract:
        return "Contract not found", 404

    # Calculate amounts
    total_amount = contract["final_budget"]
    initial_payment_amount = total_amount * 0.2
    admin_commission = total_amount * 0.05
    freelancer_amount = initial_payment_amount - admin_commission

    # Create initial payment
    payment_data = {
        "amount": initial_payment_amount,
        "paymentMode": "completed",  # Payment mode can be updated later
        "typeOfPayment": "initial",
        "paymentDetails": {},  # Placeholder for actual payment details
        "contract_id": contract["_id"],
        "jobposter_id": contract["jobposter_id"],
        "freelancer_id": contract["freelancer_id"],
        "freelancer_amount": freelancer_amount,
        "admin_commission": admin_commission,
        "created_at": datetime.now(),
    }
    Payment.insert_one(payment_data)

    # Update project details
    Project.collection.update_one(
        {"_id": contract["project_id"]},
        {
            "$set": {
                "finalFreelancer_id": contract["freelancer_id"],
                "initialPaid": True,
                "finalCost": total_amount,
                "initialPaid": True,
            }
        },
    )

    # Update contract status
    Contract.collection.update_one(
        {"_id": ObjectId(contract_id)},
        {"$set": {"status": "accepted"}},
    )

    return redirect(url_for('freelancer_contracts'))







@freelancing.route('/freelancer_payments')
def freelancer_payments():
    """
    Display payment history and earnings for freelancers.
    """
    if session.get("user_type") != "freelancer":
        return redirect(url_for('login'))

    # Fetch freelancer's payments from MongoDB
    freelancer_id = session.get("user_id")
    payments = list(Payment.find({"freelancer_id": ObjectId(freelancer_id)}))
    # print(payments)
    return render_template('freelancers/payments.html', payments=payments)





@freelancing.route('/jobposter_payments')
def jobposter_payments():
    """
    Display payment history for the job poster.
    """
    if session.get("user_type") != "jobposter":
        return redirect(url_for('login'))

    # Fetch job poster's payments from MongoDB
    jobposter_id = session.get("user_id")
    payments = list(Payment.find({"jobposter_id": ObjectId(jobposter_id)}))
    
    return render_template('jobposters/payments.html', payments=payments)



@freelancing.route('/jobposter_freelancers')
def jobposter_freelancers():
    """
    Display freelancers working for the job poster.
    """
    if session.get("user_type") != "jobposter":
        return redirect(url_for('login'))

    jobposter_id = session.get("user_id")
    
    # Fetch contracts associated with this job poster
    contracts = list(Contract.find({"jobposter_id": ObjectId(jobposter_id), "status": "accepted"}))
    
    freelancers = []
    for contract in contracts:
        freelancer = Freelancer.find_one({"_id": contract["freelancer_id"]})
        if freelancer:
            project = Project.find_one({"_id": contract["project_id"]})
            freelancers.append({
                "name": freelancer["username"],
                "email": freelancer["email"],
                "project_title": project["title"] if project else "Unknown",
                "deadline": contract["expected_date_of_completion"],
                "contract_id": str(contract["_id"])  # Include contract ID for "Mark as Done"
            })
    
    return render_template('jobposters/freelancers.html', freelancers=freelancers)


@freelancing.route('/mark_as_done/<contract_id>', methods=['POST'])
def mark_as_done(contract_id):
    """
    Mark a contract as done, create the final payment, and update project details.
    """
    if session.get("user_type") != "jobposter":
        return redirect(url_for('login'))

    # Fetch the contract details
    contract = Contract.find_one({"_id": ObjectId(contract_id)})
    if not contract:
        return "Contract not found", 404

    # Calculate amounts for the final payment
    total_amount = contract["final_budget"]
    final_payment_amount = total_amount * 0.8
    admin_commission = total_amount * 0.05
    freelancer_amount = final_payment_amount - admin_commission

    # Create final payment
    payment_data = {
        "amount": final_payment_amount,
        "paymentMode": "Completed",  # Placeholder for payment mode
        "typeOfPayment": "final",
        "paymentDetails": {},  # Placeholder for actual payment details
        "contract_id": contract["_id"],
        "jobposter_id": contract["jobposter_id"],
        "freelancer_id": contract["freelancer_id"],
        "freelancer_amount": freelancer_amount,
        "admin_commission": admin_commission,
        "created_at": datetime.now(),
    }
    Payment.insert_one(payment_data)

    # Update project details to reflect final payment
    Project.collection.update_one(
        {"_id": contract["project_id"]},
        {"$set": {"finalPaid": True}}
    )

    # Update contract status
    Contract.collection.update_one(
        {"_id": ObjectId(contract_id)},
        {"$set": {"status": "completed"}}
    )

    return redirect(url_for('jobposter_freelancers'))
