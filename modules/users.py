import streamlit as st
import sqlite3
from resume_parser import extract_resume_info_from_pdf, extract_contact_number_from_resume, extract_education_from_resume, \
    extract_experience, suggest_skills_for_job, show_colored_skills, calculate_resume_score, extract_resume_info

# Function to create a table for PDFs in SQLite database if it doesn't exist
def create_table():
    conn = sqlite3.connect('data/user_pdfs.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_uploaded_pdfs (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            data BLOB NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to insert PDF into the SQLite database
def insert_pdf(name, data):
    conn = sqlite3.connect('data/user_pdfs.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_uploaded_pdfs (name, data) VALUES (?, ?)', (name, data))
    conn.commit()
    conn.close()

# Function to generate feedback for the resume
def generate_feedback(resume_info, education_info, experience_info, skills, resume_score):
    feedback = []

    # Font & Formatting Feedback (Placeholder, need NLP model for actual implementation)
    feedback.append("📌 Consider using a professional font and consistent formatting for better readability.") 

    # Missing Sections
    if not resume_info.get('email'):
        feedback.append("📌 No email found. Ensure your email is listed on your resume.")
    if not resume_info.get('skills'):
        feedback.append("📌 No skills detected. Consider adding key skills relevant to your job.")
    if not education_info:
        feedback.append("📌 No education details found. Ensure to list your academic background.")
    if experience_info.get('level_of_experience') == "Unknown":
        feedback.append("📌 Work experience details are missing or unclear. Be specific about job titles and duration.")

    # Skill Suggestions
    if skills:
        missing_skills = suggest_skills_for_job(skills)  # Function to compare with job role requirements
        if missing_skills:
            feedback.append(f"📌 Suggested skills to add: {', '.join(missing_skills)}")

    # Resume Score-Based Feedback
    if resume_score < 50:
        feedback.append("📌 Your resume score is low. Improve clarity, formatting, and include more relevant details.")
    elif resume_score < 80:
        feedback.append("📌 Your resume is good, but consider refining skills and work experience details for a stronger profile.")

    return feedback

def process_user_mode():
    create_table()  # Ensure the table exists

    st.title("Resume Parser using NLP 📄")
    uploaded_file = st.file_uploader("Upload a PDF resume", type="pdf")

    if uploaded_file:
        st.success("✅ File uploaded successfully!")

        pdf_name = uploaded_file.name
        pdf_data = uploaded_file.getvalue()
        insert_pdf(pdf_name, pdf_data)  # Save the uploaded file to the database

        pdf_text = extract_resume_info_from_pdf(uploaded_file)
        resume_info = extract_resume_info(pdf_text)

        st.markdown('<hr>', unsafe_allow_html=True)
        st.header("🔍 Extracted Information")

# Display user details
    
        
        # Display user details
        st.write(f"**Email:** {resume_info.get('email', 'Not found')}")
        contact_number = extract_contact_number_from_resume(pdf_text)
        st.write(f"**Phone Number:** {contact_number if contact_number else 'Not found'}")

        st.markdown('<hr>', unsafe_allow_html=True)
        st.header("🎓 Education")
        education_info = extract_education_from_resume(pdf_text)
        st.write(', '.join(education_info) if education_info else "No education information found")

        st.markdown('<hr>', unsafe_allow_html=True)
        st.header("💼 Work Experience")
        experience_info = extract_experience(pdf_text)
        st.write(f"**Experience Level:** {experience_info.get('level_of_experience', 'Unknown')}")
        st.write(f"**Suggested Position:** {experience_info.get('suggested_position', 'Not available')}")

        st.markdown('<hr>', unsafe_allow_html=True)
        st.header("⚡ Skills")
        if resume_info.get('skills'):
            show_colored_skills(resume_info['skills'])
        else:
            st.warning("No skills detected. Consider adding skills relevant to your job.")

        st.markdown('<hr>', unsafe_allow_html=True)
        st.header("📊 Resume Score")
        resume_score = calculate_resume_score(resume_info)
        st.write(f"**Resume Score:** {resume_score}/100")
        st.progress(resume_score / 100)

        st.markdown('<hr>', unsafe_allow_html=True)
        st.header("📢 Feedback & Suggestions")

        feedback = generate_feedback(resume_info, education_info, experience_info, resume_info.get('skills', []), resume_score)
        for item in feedback:
            st.warning(item)


if __name__ == '__main__':
    process_user_mode()
