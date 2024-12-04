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
    Handle chatbot queries and return AI-generated responses including project details.
    """
    print(f"In chat bot")
    user_message = request.json.get("message", "").strip().lower()

    if not user_message:
        return jsonify({"reply": "I need a message to assist you. Please type something!"}), 400

    try:
        base_url = request.host_url

        # Check if the user is asking about available projects
        if "projects" in user_message or "available projects" in user_message:
            projects = Project.find({"status": "open"})  # Fetch open projects from the database

            if not projects:
                reply = "No projects are available at the moment. Please check back later!"
            else:
                # Include project details in the response
                project_details = []
                for project in projects[:5]:
                    project_id = project.get('_id', 'Unknown ID')
                    title = project.get('title', 'Unnamed Project')
                    budget = project.get('expected_cost', 'Not specified')
                    category = project.get('category_name', 'Not specified')
                    description = project.get('description', 'No description provided.')
                    deadline = project.get('deadline', 'No deadline specified')

                    # Create a detailed project summary
                    project_detail = f"""
                    <strong>{title}</strong> (Budget: {budget})<br>
                    Description: {description}<br>
                    Deadline: {deadline}<br>
                    Category: {category}<br>
                    <a href='{base_url}apply_project/{project_id}'>Apply Now</a>
                    """
                    project_details.append(project_detail.strip())

                reply = (
                    "Here are some projects you can apply for:<br><br>"
                    + "<br><br>".join(project_details)
                )

        elif any(keyword in user_message for keyword in ["about", "details", "specific"]):
            # Extract keywords from user query
            query_words = user_message.replace("about", "").replace("details", "").strip()
            keywords = [word.strip() for word in query_words.split() if word]

            if not keywords:
                reply = "Can you please provide more information about which project you want details for?"
            else:
                # Find a project that matches any of the keywords
                project = Project.find_one(
                    {"$and": [{"status": "open"}, {"title": {"$regex": "|".join(keywords), "$options": "i"}}]}
                )

                if project:
                    title = project.get('title', 'Unnamed Project')
                    budget = project.get('expected_cost', 'Not specified')
                    description = project.get('description', 'No description provided.')
                    deadline = project.get('deadline', 'No deadline specified')
                    category = project.get('category_name', 'Not specified')

                    reply = f"""
                    Here are the details for <strong>{title}</strong>:<br>
                    <strong>Budget:</strong> {budget}<br>
                    <strong>Description:</strong> {description}<br>
                    <strong>Deadline:</strong> {deadline}<br>
                    <strong>Category:</strong> {category}<br>
                    <a href='{base_url}apply_project/{project.get('_id')}'>Apply Now</a>
                    """
                else:
                    reply = f"I couldn't find a project matching '{query_words}'. Please check the project titles on the screen."

        else:
            # General AI response with guided prompts
            prompt = f"""
            You are a helpful freelancing platform assistant. Your job is to help users find projects or clarify queries about their freelance work.

            If the user mentions "projects," provide a list of projects with details like title, budget, description, and deadline. If the user asks for specific details like title or budget or description or deadline ask them for which project they need the information, and based on the title provided, if the project exists, give the details. Otherwise, inform them politely that the project isn't available. 

            For other queries, offer clear and concise responses that directly address their needs.

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