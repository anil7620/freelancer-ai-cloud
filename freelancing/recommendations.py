# import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# from freelancing.models.project import Project
# from freelancing.models.freelancer import Freelancer

# def recommend_projects(freelancer_id):
#     # Fetch freelancer details
#     freelancer = Freelancer.find_one({"_id": freelancer_id})
#     freelancer_skills = freelancer["skills"]

#     # Fetch all projects
#     projects = Project.find({"status": "open"})

#     # Create a DataFrame for projects
#     projects_df = pd.DataFrame(projects)
#     if projects_df.empty:
#         return []

#     # Use TF-IDF for skill matching
#     vectorizer = TfidfVectorizer()
#     tfidf_matrix = vectorizer.fit_transform(projects_df["description"])

#     # Calculate similarity scores
#     freelancer_vector = vectorizer.transform([freelancer_skills])
#     similarity_scores = cosine_similarity(freelancer_vector, tfidf_matrix)

#     # Sort and get top recommendations
#     projects_df["similarity"] = similarity_scores[0]
#     recommended_projects = projects_df.sort_values(by="similarity", ascending=False).head(5)
#     return recommended_projects.to_dict(orient="records")
