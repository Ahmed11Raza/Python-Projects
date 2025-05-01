import spacy
import spacy.cli
from spacy.matcher import Matcher
import re
from collections import defaultdict
import streamlit as st

# Check if model exists, download if not
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    st.info("Model 'en_core_web_sm' not found. Downloading now...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Define role categories and associated keywords
ROLE_CATEGORIES = {
    "Developer": ["python", "javascript", "java", "c++", "software", "developer", "engineer", "coding", "programming"],
    "Manager": ["manager", "management", "lead", "director", "supervisor", "project", "team", "strategy"],
    "Analyst": ["analyst", "data", "analysis", "analytics", "research", "statistics", "business"]
}

def extract_text_features(text):
    """Extract key features from resume text using spaCy"""
    doc = nlp(text.lower())
    
    # Initialize extracted data
    extracted_data = {
        "skills": set(),
        "education": [],
        "experience": []
    }
    
    # Define patterns for matcher
    matcher = Matcher(nlp.vocab)
    
    # Skill pattern (simple noun phrases)
    skill_pattern = [{"POS": "NOUN", "OP": "+"}, {"POS": "ADJ", "OP": "*"}]
    matcher.add("SKILL", [skill_pattern])
    
    # Education pattern
    edu_pattern = [{"LOWER": {"IN": ["bachelor", "master", "phd", "degree"]}}]
    matcher.add("EDUCATION", [edu_pattern])
    
    # Experience pattern
    exp_pattern = [{"LOWER": {"IN": ["years", "experience"]}}, {"POS": "NUM", "OP": "?"}]
    matcher.add("EXPERIENCE", [exp_pattern])
    
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        match_label = nlp.vocab.strings[match_id]
        
        if match_label == "SKILL":
            extracted_data["skills"].add(span.text)
        elif match_label == "EDUCATION":
            extracted_data["education"].append(span.text)
        elif match_label == "EXPERIENCE":
            extracted_data["experience"].append(span.text)
    
    return extracted_data

def categorize_resume(features):
    """Categorize resume into roles with confidence scores"""
    skills = features["skills"]
    category_scores = defaultdict(float)
    
    # Calculate scores based on skill matches
    total_matches = 0
    for category, keywords in ROLE_CATEGORIES.items():
        matches = sum(1 for skill in skills for keyword in keywords if keyword in skill)
        total_matches += matches
        category_scores[category] = matches
    
    # Normalize scores to get confidence (0-1)
    results = {}
    if total_matches > 0:
        for category, score in category_scores.items():
            confidence = score / total_matches
            if confidence > 0.2:  # Threshold for relevance
                results[category] = round(confidence, 2)
    
    return results if results else {"Uncategorized": 0.5}

def parse_and_categorize(resume_text):
    """Main function to process resume text"""
    # Basic text cleaning
    cleaned_text = re.sub(r'\s+', ' ', resume_text.strip())
    
    # Extract features
    features = extract_text_features(cleaned_text)
    
    # Categorize based on features
    categories = categorize_resume(features)
    
    return {
        "skills": list(features["skills"]),
        "education": features["education"],
        "experience": features["experience"],
        "categories": categories
    }

# Streamlit UI
def main():
    st.title("Resume Parser and Categorizer")
    st.write("Paste your resume text below to analyze skills, education, experience, and job role categorization.")

    # Text input for resume
    resume_text = st.text_area("Enter Resume Text", height=200, placeholder="e.g., Software engineer with 5 years experience in Python...")

    if st.button("Parse Resume"):
        if resume_text:
            with st.spinner("Parsing resume..."):
                result = parse_and_categorize(resume_text)
                
                # Display results
                st.subheader("Parsed Results")
                
                st.write("**Skills:**")
                st.write(", ".join(result["skills"]) if result["skills"] else "None identified")
                
                st.write("**Education:**")
                st.write(", ".join(result["education"]) if result["education"] else "None identified")
                
                st.write("**Experience:**")
                st.write(", ".join(result["experience"]) if result["experience"] else "None identified")
                
                st.write("**Role Categories (Confidence Scores):**")
                if result["categories"]:
                    for role, score in result["categories"].items():
                        st.write(f"{role}: {score}")
                else:
                    st.write("No categories assigned")
        else:
            st.warning("Please enter some resume text to parse.")

if __name__ == "__main__":
    main()
    