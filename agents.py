# agents.py
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
    You are an AI agent tasked with generating candidate resumes. Provide exactly one JSON array containing {num_resumes} resume strings. Each resume should:
    - Include a name, years of experience, a list of skills (some matching a typical Software Engineer job), and an email address.
    - Be concise (1-2 sentences).
    Format the response as a single, valid JSON array of strings enclosed in triple backticks (```) and nothing else.
    """.format(num_resumes=num_resumes)
    return extract_json_block(call_llama3(prompt))

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

def rank_resumes(job_description, resumes):
    prompt = """
    You are an AI agent tasked with ranking candidate resumes against a job description. Given:
    - Job Description: {job_description}
    - Resumes: {resumes}
    Rank the resumes based on how well they match the job requirements. Return a Markdown-formatted list with:
    - Each line as "- [Name]: [Score] - [Brief reason]"
    - Scores must be between 50 and 100, reflecting match quality.
    - No additional commentary or deviations.
    Return only the list within triple backticks (```).
    """.format(job_description=job_description, resumes='\n'.join(resumes))
    return extract_markdown_block(call_llama3(prompt))

def automate_email(resumes_with_scores, job_description):
    emails = []
    if not resumes_with_scores:
        return emails
    for resume_line in resumes_with_scores:
        if not resume_line.strip():
            continue
        try:
            if ':' not in resume_line or '-' not in resume_line:
                name, score, email = "Unknown Candidate", 0, "unknown@example.com"
            else:
                name = resume_line.split(':')[0].replace('-', '').strip()
                score = int(resume_line.split(':')[1].split('-')[0].strip() or 0)
                reason = resume_line.split('-', 1)[1].strip() if '-' in resume_line else ''
                email = reason.split('email:')[-1].strip() if 'email:' in reason else f"{name.lower().replace(' ', '.')}@example.com"

            message_type = "interview_invite" if score >= 70 else "rejection"
            subject = f"{message_type.replace('_', ' ').title()} for {job_description.split('\n')[0].replace('#', '').strip()}"
            body = f"Dear {name},\n{'We invite you to an interview.' if message_type == 'interview_invite' else 'We won’t be moving forward.'}\nBest regards,\n[Your Name]"

            emails.append({
                "status": "success",
                "to": email,
                "cc": "hiring.team@example.com",
                "subject": subject,
                "message": "Email sent successfully",
                "body": body.strip()
            })
        except (IndexError, ValueError) as e:
            print(f"Failed to parse resume: {resume_line} - {str(e)}")
            continue
    return emails

def schedule_interview(resumes_with_scores, interview_times):
    confirmations = []
    for resume_line, interview_time in zip(resumes_with_scores, interview_times):
        if not resume_line.strip() or not interview_time:
            continue
        name = resume_line.split(':')[0].replace('-', '').strip()
        email = resume_line.split('email:')[-1].strip() if 'email:' in resume_line else f"{name.lower().replace(' ', '.')}@example.com"
        
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
    return confirmations

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