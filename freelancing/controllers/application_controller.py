import os
from flask import jsonify, request
from freelancing import freelancing
import google.generativeai as genai
from freelancing.models.project import Project

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
    Handle chatbot queries for the 'Apply for Project' page and provide contextual responses.
    """
    user_message = request.json.get("message", "").strip().lower()

    if not user_message:
        return jsonify({"reply": "I need a message to assist you. Please type something!"}), 400

    try:
        # Fetch project details using project_id
        project = Project.find_one({"_id": ObjectId(project_id)})
        if not project:
            return jsonify({"reply": "Sorry, I couldn't find the project details."}), 404

        # Extract project details
        project_title = project.get("title", "Unnamed Project")
        project_budget = project.get("expected_cost", "Not specified")
        project_deadline = project.get("deadline", "Not specified")
        project_description = project.get("description", "No description available")
        project_category = project.get("category_name", "Not categorized")

        # Handle specific queries
        if "budget" in user_message:
            reply = f"The budget for the project '{project_title}' is ${project_budget}."
        elif "deadline" in user_message or "due date" in user_message:
            reply = f"The deadline for the project '{project_title}' is {project_deadline}."
        elif "description" in user_message:
            reply = f"Description for '{project_title}': {project_description}"
        elif "category" in user_message:
            reply = f"This project belongs to the category: {project_category}."
        elif "details" in user_message or "all info" in user_message:
            # Provide a summary of all project details
            reply = f"""
            Here are the details for the project '{project_title}':
            - **Category**: {project_category}
            - **Budget**: ${project_budget}
            - **Deadline**: {project_deadline}
            - **Description**: {project_description}
            """
        else:
            # General fallback using AI
            prompt = f"""
            You are assisting a user with a project titled '{project_title}'.
            Project details:
            - Category: {project_category}
            - Budget: ${project_budget}
            - Deadline: {project_deadline}
            - Description: {project_description}

            User Query: {user_message}

            Respond clearly and concisely with a helpful answer.
            """
            response = google_model.generate_content(prompt)
            reply = response.text.strip()[:200]  # Keep responses concise

        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Unexpected Error: {e}")
        return jsonify({"reply": "I'm having trouble understanding your query. Can you clarify?"}), 500
