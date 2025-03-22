# agents.py
import json
import logging
import random
from utils import call_llama3, extract_markdown_block, extract_json_block

def generate_hiring_requirements():
    prompt = """
    You are an AI agent tasked with generating hiring requirements for a single job. Provide exactly one JSON object with:
    - job_title (e.g., 'Data Analyst', 'Web Developer')
    - skills (list of 4-6 relevant skills)
    - experience_level ('Entry', 'Mid', or 'Senior')
    Format the response as a single, valid JSON string enclosed in triple backticks (```) and nothing else.
    """
    return extract_json_block(call_llama3(prompt))

def generate_resumes(num_resumes=None):
    num_resumes = random.randint(5, 10) if num_resumes is None else num_resumes
    prompt = """
    You are an AI agent tasked with generating candidate resumes. Provide exactly one JSON array containing {num_resumes} resume objects. Each resume object should:
    - Include a name, years of experience, a list of skills (some matching a typical Software Engineer job), and an email address.
    - Be concise (1-2 sentences).
    Format the response as a single, valid JSON array of objects enclosed in triple backticks (```) and nothing else.
    Example: ```
    [
        {{
            "name": "John Doe",
            "yearsOfExperience": 5,
            "skills": ["Java", "Python", "SQL"],
            "email": "john.doe@example.com"
        }},
        {{
            "name": "Jane Smith",
            "yearsOfExperience": 3,
            "skills": ["JavaScript", "React", "Node.js"],
            "email": "jane.smith@example.com"
        }}
    ]
    ```
    """.format(num_resumes=num_resumes)

    try:
        # Call the LLaMA3 model
        llama3_response = call_llama3(prompt)

        # Log the raw response for debugging
        logging.debug(f"LLaMA3 response: {llama3_response}")

        # Extract the JSON block from the response
        resumes = extract_json_block(llama3_response)

        # Validate that the response is a list of dictionaries
        if not isinstance(resumes, list) or not all(isinstance(r, dict) for r in resumes):
            raise ValueError("Invalid response format: Expected a list of dictionaries.")

        return resumes
    except Exception as e:
        logging.error(f"Error in generate_resumes: {str(e)}")
        return {"error": f"Server error: {str(e)}"}
    
def generate_jd(job_title, skills, experience_level):
    prompt = f"""
    You are an AI agent for generating job descriptions. Create a detailed job description for:
    - Job Title: {job_title}
    - Required Skills: {', '.join(skills)}
    - Experience Level: {experience_level}
    The output should be in markdown format, including sections for 'Overview', 'Responsibilities', 'Qualifications', and 'Benefits'.
    Return the job description as plain text without additional commentary.
    """
    return call_llama3(prompt)

import logging

def rank_resumes(job_description, resumes):
    try:
        # Log the input resumes for debugging
        logging.debug(f"Input resumes: {resumes}")

        # Validate that resumes is a list of dictionaries
        if not isinstance(resumes, list) or not all(isinstance(r, dict) for r in resumes):
            raise ValueError("Resumes must be a list of dictionaries.")

        # Convert the resumes list to a string for the prompt
        resumes_str = '\n'.join([json.dumps(resume) for resume in resumes])

        # Log the constructed resumes_str for debugging
        logging.debug(f"Constructed resumes_str: {resumes_str}")

        # Construct the prompt
        prompt = f"""
        You are an AI agent tasked with ranking candidate resumes against a job description. Given:
        - Job Description: {job_description}
        - Resumes: {resumes_str}
        Rank the resumes based on how well they match the job requirements. Return a JSON array where each object contains:
        - "name" (string): the candidate's name
        - "score" (integer): a score between 50 and 100 reflecting match quality
        - "reason" (string): a brief reason for the score
        Format the response as a single, valid JSON array enclosed in triple backticks (```) and nothing else.
        Example: ```
        [
            {{"name": "John Doe", "score": 85, "reason": "Strong match with Python and Java skills"}},
            {{"name": "Jane Smith", "score": 70, "reason": "Good match but lacks experience in cloud computing"}}
        ]
        ```
        """

        # Log the constructed prompt for debugging
        logging.debug(f"Constructed prompt: {prompt}")

        # Call the LLaMA3 model
        llama3_response = call_llama3(prompt)

        # Log the LLaMA3 response for debugging
        logging.debug(f"LLaMA3 response: {llama3_response}")

        # Extract the JSON block from the response
        ranked_resumes = extract_json_block(llama3_response)

        return ranked_resumes
    except Exception as e:
        logging.error(f"Error in rank_resumes: {str(e)}")
        raise ValueError(f"Error ranking resumes: {str(e)}")
        logging.error(f"Error in rank_resumes: {str(e)}")
        raise ValueError(f"Error ranking resumes: {str(e)}")
    
def automate_email(ranked_resumes, job_description):
    """
    Simulates sending emails to candidates based on their ranking.
    
    Args:
        ranked_resumes (list): A list of ranked resumes, each containing:
            - "name" (str): Candidate's name
            - "score" (int): Candidate's score
            - "reason" (str): Reason for the score
        job_description (str): The job description.
    
    Returns:
        list: A list of simulated email responses.
    """
    try:
        # Log the input for debugging
        logging.debug(f"Ranked resumes: {ranked_resumes}")
        logging.debug(f"Job description: {job_description}")

        # Extract job title from the first line of job_description
        job_title = job_description.splitlines()[0].replace('#', '').strip()

        # Simulate sending emails
        emails = []
        for resume in ranked_resumes:
            try:
                name = resume.get("name", "Unknown Candidate")
                score = resume.get("score", 0)
                reason = resume.get("reason", "")
                email = resume.get("email", f"{name.lower().replace(' ', '.')}@example.com")

                # Determine the email type based on the score
                if score >= 70:
                    message_type = "Interview Invitation"
                    subject = f"{message_type} for {job_title}"
                    body = f"Dear {name},\n\nWe are pleased to invite you for an interview for the position of {job_title}.\n\nBest regards,\nHiring Team"
                else:
                    message_type = "Application Update"
                    subject = f"{message_type} for {job_title}"
                    body = f"Dear {name},\n\nThank you for applying. Unfortunately, we will not be moving forward with your application.\n\nBest regards,\nHiring Team"

                # Simulate the email response
                emails.append({
                    "status": "success",
                    "to": email,
                    "cc": "hiring.team@example.com",
                    "subject": subject,
                    "body": body,
                    "message": "Email sent successfully"
                })
            except Exception as e:
                logging.error(f"Error processing resume {resume}: {str(e)}")
                emails.append({
                    "status": "error",
                    "to": "unknown@example.com",
                    "cc": "hiring.team@example.com",
                    "subject": "Error: Failed to send email",
                    "body": "An error occurred while processing this candidate.",
                    "message": str(e)
                })

        return emails
    except Exception as e:
        logging.error(f"Error in automate_email: {str(e)}")
        return [{
            "status": "error",
            "to": "unknown@example.com",
            "cc": "hiring.team@example.com",
            "subject": "Error: Failed to send emails",
            "body": "An error occurred while processing the email automation.",
            "message": str(e)
        }]
        
def schedule_interview(ranked_resumes, interview_times):
    """
    Simulates scheduling interviews for candidates.
    
    Args:
        ranked_resumes (list): A list of ranked resumes, each containing:
            - "name" (str): Candidate's name
            - "email" (str): Candidate's email address
        interview_times (list): A list of interview times corresponding to the candidates.
    
    Returns:
        list: A list of simulated interview confirmations.
    """
    try:
        # Log the input for debugging
        logging.debug(f"Ranked resumes: {ranked_resumes}")
        logging.debug(f"Interview times: {interview_times}")

        # Simulate scheduling interviews
        confirmations = []
        for resume, interview_time in zip(ranked_resumes, interview_times):
            try:
                name = resume.get("name", "Unknown Candidate")
                email = resume.get("email", f"{name.lower().replace(' ', '.')}@example.com")

                # Simulate the confirmation response
                confirmations.append({
                    "status": "success",
                    "to": email,
                    "cc": "hiring.team@example.com",
                    "event": {
                        "title": "Interview with Candidate",
                        "time": interview_time,
                        "link": f"https://mockcalendar.example.com/invite/{name.lower().replace(' ', '.')}-{interview_time.replace(':', '-')}"
                    },
                    "message": "Calendar event created successfully"
                })
            except Exception as e:
                logging.error(f"Error processing resume {resume}: {str(e)}")
                confirmations.append({
                    "status": "error",
                    "to": "unknown@example.com",
                    "cc": "hiring.team@example.com",
                    "event": {
                        "title": "Error: Failed to schedule interview",
                        "time": "N/A",
                        "link": "N/A"
                    },
                    "message": str(e)
                })

        return confirmations
    except Exception as e:
        logging.error(f"Error in schedule_interview: {str(e)}")
        return [{
            "status": "error",
            "to": "unknown@example.com",
            "cc": "hiring.team@example.com",
            "event": {
                "title": "Error: Failed to schedule interviews",
                "time": "N/A",
                "link": "N/A"
            },
            "message": str(e)
        }]

def conduct_interview(job_description, candidate_response=None):
    prompt = f"""
    You are a friendly, human-like AI interviewer. Given this job description:
    {job_description}
    {'Previous candidate response: ' + candidate_response if candidate_response else 'Start with a warm, welcoming initial question.'}
    Ask a thoughtful, conversational question tailored to the job requirements. Return the question in Markdown format within triple backticks (```) and nothing else.
    """
    return extract_markdown_block(call_llama3(prompt))

def recommend_hire(interview_transcript):
    prompt = f"""
    You are an AI agent for making hiring recommendations. Given this interview transcript:
    {interview_transcript}
    Analyze the candidate's responses and provide:
    - Strengths
    - Weaknesses
    - Hire/No-Hire decision
    Return the analysis in markdown format without additional commentary.
    """
    return call_llama3(prompt)

def generate_sample_transcript(top_candidate, job_description, chat_transcript=None):
    chat_transcript_value = chat_transcript or 'None'
    prompt = """
    You are an AI simulating a video/audio interview. Given:
    - Candidate: {top_candidate}
    - Job Description: {job_description}
    - Optional Chat Transcript: {chat_transcript_value}
    Generate a concise video/audio-style interview transcript (10-15 lines) with alternating AI and candidate responses. Include verbal cues (e.g., *laughs*, *pauses*). Return as plain text within triple backticks (```) and nothing else.
    """.format(top_candidate=top_candidate, job_description=job_description, chat_transcript_value=chat_transcript_value)
    return extract_markdown_block(call_llama3(prompt))

def analyze_sentiment(interview_transcript):
    prompt = f"""
    You are an AI agent for sentiment analysis. Given this interview transcript:
    {interview_transcript}
    Analyze the sentiment and emotional tone, indicating:
    - Confidence level (High, Medium, Low)
    - Emotional tone (e.g., Positive, Neutral, Negative)
    Return the analysis in markdown format without additional commentary.
    """
    return call_llama3(prompt)