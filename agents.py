# agents.py
import json
import logging
import random
import time
from utils import call_llama3, extract_markdown_block, extract_json_block

def generate_hiring_requirements():
    prompt = f"""
    You are an AI agent tasked with generating hiring requirements for a single job. Generate exactly one JSON object containing:
    - job_title (e.g., 'Data Analyst', 'Web Developer')
    - skills (list of 4-6 relevant skills)
    - experience_level ('Entry', 'Mid', or 'Senior')
    Return only one valid JSON object enclosed in triple backticks (```) with no additional objects, text, comments, or examples outside the JSON.
    Example format (for reference, do not include in output):
    ```
    {{"job_title": "Data Scientist", "skills": ["Python", "SQL", "Machine Learning", "Statistics"], "experience_level": "Mid"}}
    ```
    Start with ``` and end with ```.
    """
    return extract_json_block(call_llama3(prompt))

def generate_resumes(job_description, num_resumes=None):
    num_resumes = random.randint(5, 10) if num_resumes is None else num_resumes
    if num_resumes < 1:
        num_resumes = 1

    prompt = """
    You are an AI agent tasked with generating candidate resumes based on a job description. Given:
    - Job Description: {job_description}
    Generate exactly one JSON array containing {num_resumes} resume objects. Each resume object must:
    - Include a name, years of experience (1-12), a list of 3-5 skills (some matching the skills in the job description), and an email address based on the name (e.g., firstname.lastname@example.com).
    - Be concise (1-2 sentences).
    - **Do not use "John Doe" or "Jane Smith" as names**, as these are just examples.
    - **Return only the JSON array enclosed in triple backticks (```) with no additional text, comments, or examples outside the JSON.**
    Example format (for reference, do not include this in the output):
    [
        {{"name": "Michael Brown", "yearsOfExperience": 8, "skills": ["Python", "AWS", "Docker"], "email": "michael.brown@example.com"}},
        {{"name": "Sarah Lee", "yearsOfExperience": 4, "skills": ["JavaScript", "React", "SQL"], "email": "sarah.lee@example.com"}}
    ]
    Start your response with ``` and end with ```.
    """.format(job_description=job_description, num_resumes=num_resumes)

    try:
        # Call the LLaMA3 model
        llama3_response = call_llama3(prompt)
        logging.debug(f"LLaMA3 response: {llama3_response}")

        # Extract the JSON block from the response
        resumes = extract_json_block(llama3_response)

        # Validate that the response is a list of dictionaries
        if not isinstance(resumes, list) or not all(isinstance(r, dict) for r in resumes):
            raise ValueError("Invalid response format: Expected a list of dictionaries.")

        # Filter out "John Doe" and "Jane Smith" if they appear
        forbidden_names = {"John Doe", "Jane Smith"}
        filtered_resumes = []
        replacement_count = 0

        for resume in resumes:
            name = resume.get("name", "")
            if name in forbidden_names:
                replacement_count += 1
                new_name = f"Candidate {replacement_count}"
                filtered_resumes.append({
                    "name": new_name,
                    "yearsOfExperience": random.randint(1, 12),
                    "skills": random.sample(
                        ["Python", "Java", "JavaScript", "React", "Node.js", "SQL", "C++", "AWS", "Docker", "Ruby"],
                        k=random.randint(3, 5)
                    ),
                    "email": f"{new_name.lower().replace(' ', '.')}@example.com"
                })
            else:
                filtered_resumes.append(resume)

        # Ensure we have the requested number of resumes
        while len(filtered_resumes) < num_resumes:
            replacement_count += 1
            new_name = f"Candidate {replacement_count}"
            filtered_resumes.append({
                "name": new_name,
                "yearsOfExperience": random.randint(1, 12),
                "skills": random.sample(
                    ["Python", "Java", "JavaScript", "React", "Node.js", "SQL", "C++", "AWS", "Docker", "Ruby"],
                    k=random.randint(3, 5)
                ),
                "email": f"{new_name.lower().replace(' ', '.')}@example.com"
            })

        # Trim to requested number
        filtered_resumes = filtered_resumes[:num_resumes]

        logging.debug(f"Final resumes tailored to job description: {filtered_resumes}")
        return filtered_resumes

    except Exception as e:
        logging.error(f"Error in generate_resumes: {str(e)}")
        # Fallback with generic candidates
        fallback_resumes = [
            {
                "name": f"Candidate {i+1}",
                "yearsOfExperience": random.randint(1, 12),
                "skills": random.sample(
                    ["Python", "Java", "JavaScript", "React", "Node.js", "SQL", "C++", "AWS", "Docker", "Ruby"],
                    k=random.randint(3, 5)
                ),
                "email": f"candidate.{i+1}@example.com"
            } for i in range(num_resumes)
        ]
        return fallback_resumes
    
def generate_jd(job_title, skills, experience_level):
    prompt = f"""
    You are an AI agent for generating job descriptions. Create exactly one detailed job description for:
    - Job Title: {job_title}
    - Required Skills: {', '.join(skills)}
    - Experience Level: {experience_level}
    The output must be a single job description in markdown format with sections: 'Overview', 'Responsibilities', 'Qualifications', and 'Benefits'.
    Return the job description as plain text enclosed in triple backticks (```) with no additional job descriptions, commentary, or examples.
    Start with ``` and end with ```.
    """
    return extract_markdown_block(call_llama3(prompt))

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
    
def automate_email(ranked_resumes, job_description):
    """
    Simulates sending personalized emails to candidates using AI-generated content.
    
    Args:
        ranked_resumes (list): A list of ranked resumes, each containing:
            - "name" (str): Candidate's name
            - "score" (int): Candidate's score
            - "reason" (str): Reason for the score
            - "email" (str): Candidate's email
        job_description (str): The job description.
    
    Returns:
        list: A list of simulated email API responses.
    """
    try:
        logging.debug(f"Ranked resumes: {ranked_resumes}")
        logging.debug(f"Job description: {job_description}")

        # Batch all candidates into a single prompt
        candidates_str = '\n'.join(
            [f"- {r['name']}: Score {r.get('score', 0)}, Reason: {r.get('reason', 'N/A')}" 
             for r in ranked_resumes]
        )
        prompt = f"""
        You are an AI agent tasked with drafting personalized emails for job candidates. Given:
        - Job Description: {job_description}
        - Candidates:
        {candidates_str}
        Generate a JSON array of email objects, one for each candidate, with:
        - "name" (string): candidate's name
        - "subject" (string): email subject
        - "body" (string): email body
        - If score >= 70, draft an interview invitation with a positive tone.
        - If score < 70, draft a polite rejection.
        - **Return only the JSON array enclosed in triple backticks (```) with no additional text, comments, or examples outside the JSON.**
        Example format (for reference, do not include in output):
        [
            {{"name": "Ethan Kim", "subject": "Interview Invitation", "body": "Dear Ethan Kim,\\n\\nWe are pleased to invite you..."}},
            {{"name": "Ava Patel", "subject": "Application Update", "body": "Dear Ava Patel,\\n\\nThank you for applying..."}}
        ]
        Start your response with ``` and end with ```.
        """
        
        # Retry logic for throttling or incomplete response
        max_retries = 3
        for attempt in range(max_retries):
            try:
                llama3_response = call_llama3(prompt)
                logging.debug(f"Email generation response: {llama3_response}")
                email_contents = extract_json_block(llama3_response)
                
                if not isinstance(email_contents, list):
                    raise ValueError("Invalid email content format: Expected a list")
                
                # Map email content to candidates
                email_map = {e["name"]: e for e in email_contents if "name" in e}
                emails = []
                job_title = job_description.splitlines()[0].replace('#', '').strip()

                for resume in ranked_resumes:
                    name = resume.get("name", "Unknown Candidate")
                    email = resume.get("email", f"{name.lower().replace(' ', '.')}@example.com")
                    score = resume.get("score", 0)
                    email_content = email_map.get(name)

                    if email_content and "subject" in email_content and "body" in email_content:
                        emails.append({
                            "status": "success",
                            "to": email,
                            "cc": "hiring.team@example.com",
                            "subject": email_content["subject"],
                            "body": email_content["body"] + "\nHiring Team",  # Complete the body if truncated
                            "message": "Email sent successfully via simulated API"
                        })
                    else:
                        # Fallback for individual candidate if missing from response
                        if score >= 70:
                            subject = f"Interview Invitation for {job_title}"
                            body = f"Dear {name},\n\nWe are pleased to invite you for an interview for {job_title}.\n\nBest regards,\nHiring Team"
                        else:
                            subject = f"Application Update for {job_title}"
                            body = f"Dear {name},\n\nThank you for applying. We will not be moving forward at this time.\n\nBest regards,\nHiring Team"
                        emails.append({
                            "status": "success",
                            "to": email,
                            "cc": "hiring.team@example.com",
                            "subject": subject,
                            "body": body,
                            "message": "Email sent successfully via simulated API (individual fallback)"
                        })
                return emails
            
            except Exception as e:
                if "ThrottlingException" in str(e) and attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logging.warning(f"Throttling detected, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                logging.error(f"Error generating emails: {str(e)}")
                # Batch fallback only on final failure
                emails = []
                job_title = job_description.splitlines()[0].replace('#', '').strip()
                for resume in ranked_resumes:
                    name = resume.get("name", "Unknown Candidate")
                    email = resume.get("email", f"{name.lower().replace(' ', '.')}@example.com")
                    score = resume.get("score", 0)
                    if score >= 70:
                        subject = f"Interview Invitation for {job_title}"
                        body = f"Dear {name},\n\nWe are pleased to invite you for an interview for {job_title}.\n\nBest regards,\nHiring Team"
                    else:
                        subject = f"Application Update for {job_title}"
                        body = f"Dear {name},\n\nThank you for applying. We will not be moving forward at this time.\n\nBest regards,\nHiring Team"
                    emails.append({
                        "status": "success",
                        "to": email,
                        "cc": "hiring.team@example.com",
                        "subject": subject,
                        "body": body,
                        "message": "Email sent successfully via simulated API (batch fallback)"
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
        
def schedule_interview(ranked_resumes, interview_times=None):
    """
    Simulates scheduling interviews for candidates using an AI agent to propose times.
    
    Args:
        ranked_resumes (list): A list of ranked resumes, each containing:
            - "name" (str): Candidate's name
            - "email" (str): Candidate's email address
            - "score" (int): Candidate's score (used to filter interviewees)
        interview_times (list, optional): Predefined times from frontend; if None, AI generates them.
    
    Returns:
        list: A list of simulated interview confirmations with calendar event details.
    """
    try:
        logging.debug(f"Ranked resumes: {ranked_resumes}")
        logging.debug(f"Provided interview times: {interview_times}")

        # Filter candidates with score >= 70 (interview-worthy)
        interviewees = [r for r in ranked_resumes if r.get("score", 0) >= 70]
        if not interviewees:
            raise ValueError("No candidates eligible for interviews (score >= 70)")

        # If interview_times provided, use them; otherwise, generate with AI
        if interview_times and len(interview_times) >= len(interviewees):
            proposed_times = interview_times[:len(interviewees)]
        else:
            # Simulate candidate availability and generate times with AI
            candidates_str = '\n'.join(
                [f"- {r['name']}: Score {r.get('score', 0)}, Email: {r.get('email', r['name'].lower().replace(' ', '.') + '@example.com')}" 
                 for r in interviewees]
            )
            prompt = f"""
            You are an AI agent tasked with scheduling interviews. Given:
            - Candidates (eligible for interviews):
            {candidates_str}
            - Current date: {time.strftime('%Y-%m-%d')}
            Propose interview times for each candidate within the next 7 days (Monday-Friday, 9 AM - 5 PM EST).
            - Format times as 'YYYY-MM-DDTHH:MM' (e.g., '2025-03-25T10:00').
            - Ensure no time conflicts (unique times for each candidate).
            - Return only a JSON array of objects with "name" and "time", enclosed in triple backticks (```) with no extra text.
            Example format:
            ```
            [
                {{"name": "Ethan Ellis", "time": "2025-03-25T10:00"}},
                {{"name": "Mason Kim", "time": "2025-03-26T14:00"}}
            ]
            ```
            Start with ``` and end with ```.
            """

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    llama3_response = call_llama3(prompt)
                    logging.debug(f"AI scheduling response: {llama3_response}")
                    time_slots = extract_json_block(llama3_response)
                    
                    if not isinstance(time_slots, list) or not all("name" in t and "time" in t for t in time_slots):
                        raise ValueError("Invalid time slots format")
                    
                    proposed_times = [slot["time"] for slot in time_slots]
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logging.warning(f"Scheduling attempt {attempt + 1} failed: {str(e)}, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    # Fallback to random times if AI fails
                    proposed_times = []
                    base_date = time.strptime("2025-03-24", "%Y-%m-%d")
                    for i in range(len(interviewees)):
                        day_offset = random.randint(0, 4)  # Mon-Fri
                        hour = random.randint(9, 16)  # 9 AM - 4 PM
                        slot = time.strftime("%Y-%m-%dT%H:00", time.localtime(time.mktime(base_date) + (day_offset * 86400) + (hour * 3600)))
                        proposed_times.append(slot)

        # Simulate Google Calendar integration
        confirmations = []
        for resume, interview_time in zip(interviewees, proposed_times):
            try:
                name = resume.get("name", "Unknown Candidate")
                default_email = f"{name.lower().replace(' ', '.')}@example.com"
                email = resume.get("email", default_email)

                # Mock calendar event creation
                event_link = f"https://mockcalendar.example.com/invite/{name.lower().replace(' ', '.')}-{interview_time.replace(':', '-')}"
                confirmations.append({
                    "status": "success",
                    "to": email,
                    "cc": "hiring.team@example.com",
                    "event": {
                        "title": f"Interview with {name}",
                        "time": interview_time,
                        "link": event_link
                    },
                    "message": "Calendar event created successfully via simulated Google Calendar API"
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
    Analyze the sentiment and emotional tone in exactly two concise lines:
    - Confidence level: High, Medium, or Low
    - Emotional tone: Positive, Neutral, or Negative
    Return the analysis in markdown format within triple backticks (```) with no additional text or explanations.
    Start with ``` and end with ```.
    """
    return extract_markdown_block(call_llama3(prompt))
