import os
from flask import jsonify, request
from freelancing import freelancing
import google.generativeai as genai
from freelancing.models.project import Project
from bson.objectid import ObjectId

# Configure Google Generative AI
genai.configure(api_key="AIzaSyBy9vT1HPBz1p7iqPzoyql8sNuVQFpHX_4")
google_model = genai.GenerativeModel("gemini-1.5-flash")


@freelancing.route('/chatbot', methods=['POST'])
def chatbot():
    """
    Handle chatbot queries and return AI-generated responses using Google Generative AI.
    """
    user_message = request.json.get("message", "").strip().lower()

    if not user_message:
        return jsonify({"reply": "I need a message to assist you. Please type something!"}), 400

    try:
        # Check if the user is asking about available projects
        if "projects" in user_message or "available projects" in user_message:
            base_url = request.host_url
            projects = Project.find({"status": "open"})
            if not projects:
                reply = "No projects are available at the moment. Please check back later!"
            else:
                project_links = [
                    f"<a href='{base_url}apply_project/{project['_id']}'>{project.get('title', 'Unnamed Project')}</a>"
                    for project in projects[:5]
                ]
                reply = (
                    "Here are some projects you can apply for:<br>" + "<br>".join(project_links)
                )
        else:
            # General AI response with guided prompts
            prompt = f"""
            You are a helpful freelancing platform assistant. Your job is to help users find projects or clarify queries about their freelance work. 

            If the user mentions "projects," provide a list of projects if available. For other queries, offer clear and concise responses that directly address their needs.

            User Query: {user_message}

            Respond concisely in less than 100 words.
            """
            response = google_model.generate_content(prompt)
            reply = response.text.strip()[:300]  # Truncate long replies for clarity

        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Unexpected Error: {e}")
        return jsonify({"reply": "I'm having some trouble understanding you. Can you please clarify?"}), 500



@freelancing.route('/apply_project_chatbot/<project_id>', methods=['POST'])
def apply_project_chatbot(project_id):
    """
    Handle chatbot queries for project-specific details.
    """
    user_message = request.json.get("message", "").strip().lower()

    if not user_message:
        return jsonify({"reply": "Please type your question to proceed!"}), 400

    project = Project.find_one({"_id": ObjectId(project_id)})
    if not project:
        return jsonify({"reply": "Sorry, I couldn't find this project."}), 404

    project_title = project.get("title", "Unnamed Project")
    project_description = project.get("description", "No description available.")
    project_budget = project.get("expected_cost", "Not specified")
    project_deadline = project.get("deadline", "Not specified")

    if "budget" in user_message:
        reply = f"The budget for '{project_title}' is ${project_budget}."
    elif "deadline" in user_message:
        reply = f"The deadline for '{project_title}' is {project_deadline}."
    elif "description" in user_message:
        reply = f"Description: {project_description}"
    else:
        reply = f"Details for '{project_title}':\nBudget: ${project_budget}\nDeadline: {project_deadline}"

    return jsonify({"reply": reply})

# ////////////////////////////////////////////// //
@freelancing.route('/generate_project_description', methods=['POST'])
def generate_project_description():
    """
    Generate a project description with detailed features using AI based on the project title.
    """
    project_title = request.json.get("title", "").strip()

    if not project_title:
        return jsonify({"error": "Project title is required to generate a description."}), 400

    try:
        # Use AI to generate the description with feature-specific details
        prompt = f"""
        Generate a professional project description with features based on the project title '{project_title}'.
        Include possible features, functionality, and modules that would be expected in such a project. 
        Make the description clear, structured, and user-friendly.
        """
        response = google_model.generate_content(prompt)
        description = response.text.strip()

        return jsonify({"description": description})
    except Exception as e:
        print(f"Error generating project description: {e}")
        return jsonify({"error": "Failed to generate project description. Please try again."}), 500

# ////////////////////////////////////////////// //