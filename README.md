# Recruitment AI System

## Overview

This is an AI-driven recruitment system built for the Llama Agentic AI Recruitment Challenge. It leverages Llama 3.x (via AWS Bedrock) to automate the hiring process through seven specialized AI agents. The system is designed for deployment on AWS Elastic Beanstalk, with a modular backend structure and a responsive frontend. GitHub Actions can be configured for CI/CD automation.

## Agent Functionality

1. **JD Generator**: Generates detailed job descriptions from job title, skills, and experience level inputs.
2. **ResumeRanker**: Evaluates and ranks candidate resumes based on job description fit.
3. **Email Automation**: Simulates sending personalized emails (e.g., interview invites or rejections).
4. **InterviewScheduler**: Schedules interviews with mock calendar integration.
5. **InterviewAgent**: Conducts interactive, adaptive AI-driven interviews.
6. **HireRecommendationAgent**: Analyzes interview transcripts to recommend hiring decisions.
7. **SentimentAnalyzer**: Assesses sentiment and emotional tone from interview transcripts.

## Llama 3.x Integration

All AI functionalities are powered by Llama 3.x, accessed through AWS Bedrock. Prompts are carefully designed to produce consistent, markdown-formatted outputs, fulfilling the challenge's requirement for Llama integration.

## REST API Endpoints

The system provides the following RESTful endpoints:

| Endpoint                      | Method | Description                             | Request Body (JSON) Example                                                                                      | Response (JSON) Example                                                                         |
| ----------------------------- | ------ | --------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `/`                           | GET    | Serves the frontend HTML page           | N/A                                                                                                              | HTML content                                                                                    |
| `/test`                       | GET    | Verifies server status                  | N/A                                                                                                              | `{"message": "Server is alive!"}`                                                               |
| `/generate_requirements`      | GET    | Generates sample hiring requirements    | N/A                                                                                                              | `{"job_title": "Web Developer", "skills": ["Python", "JavaScript"], "experience_level": "Mid"}` |
| `/generate_resumes`           | POST    | Generates 5-10 sample resumes           | N/A                                                                                                              | `{"resumes": ["Jane Doe, 4 years...", "John Smith, 2 years..."]}`                               |
| `/generate_jd`                | POST   | Creates a job description               | `{"job_title": "Software Engineer", "skills": ["Python", "SQL"], "experience_level": "Mid"}`                     | `{"job_description": "# Software Engineer\n..."}`                                               |
| `/rank_resumes`               | POST   | Ranks resumes against a job description | `{"job_description": "# Software Engineer\n...", "resumes": ["Jane Doe, 4 years...", "John Smith, 2 years..."]}` | `{"ranked_resumes": "- Jane Doe: 90...\n- John Smith: 60..."}`                                  |
| `/automate_email`             | POST   | Simulates email automation              | `{"ranked_resumes": "- Jane Doe: 90...\n- John Smith: 60...", "job_description": "# Software Engineer\n..."}`    | `[{"status": "success", "to": "jane.doe@example.com", "subject": "Interview Invite"}] `         |
| `/schedule_interview`         | POST   | Schedules interviews (mock)             | `{"ranked_resumes": "- Jane Doe: 90...", "interview_times": ["2025-03-25T10:00"]}`                               | `[{"status": "success", "to": "jane.doe@example.com", "event": {"time": "..."}]}`               |
| `/conduct_interview`          | POST   | Generates interview questions           | `{"job_description": "# Software Engineer\n...", "candidate_response": "I have 4 years..."}`                     | `{"question": "Can you describe a challenging project?"}`                                       |
| `/recommend_hire`             | POST   | Provides hiring recommendation          | `{"interview_transcript": "AI: Tell me... Candidate: I’m Jane..."}`                                              | `{"recommendation": "# Candidate Analysis\n- Strengths: ..."}`                                  |
| `/generate_sample_transcript` | POST   | Creates a sample interview transcript   | `{"top_candidate": "Jane Doe", "job_description": "# Software Engineer\n...", "chat_transcript": null}`          | `{"transcript": "AI: Hey Jane... Jane: Oh, hi!..."}`                                            |
| `/analyze_sentiment`          | POST   | Analyzes sentiment of a transcript      | `{"interview_transcript": "AI: Tell me... Candidate: I’m Jane..."}`                                              | `{"sentiment": "- Confidence: High\n- Tone: Positive"}`                                         |

## Setup & Execution (Local)

1. **Prerequisites**:

   - Python 3.9.18 (verified with `python --version`)
   - AWS credentials configured for Bedrock access (`aws configure`)
   - Project structure:
     ```
     /llama3-recruitment-app
      ├── README.md
      ├── agents.py
      ├── app.py
      ├── requirements.txt
      ├── static
      │   └── js
      │       └── main.js
      ├── templates
      │   └── index.html
      ├── utils.py
      └── video.mp4
     ```

2. **Installation**:

```
pip install -r requirements.txt
```

3. **Run**:

```
python app.py
```

Open `http://localhost:5000` in your browser.

## Deployment (AWS Elastic Beanstalk)

Deploy the app to AWS Elastic Beanstalk for a live demo:

1. **Prerequisites**:

- AWS CLI (`pip install awscli`)
- EB CLI (`pip install awsebcli`)
- Git initialized in the project directory

2. **Configuration**:

- Ensure `requirements.txt`:
  ```
  Flask==2.3.3
  Flask-Cors==4.0.0
  boto3==1.28.85
  gunicorn==20.1.0
  ```
- Create `.ebextensions/python.config`:
  ```
  option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app:app
  aws:elasticbeanstalk:environment:proxy:
    ProxyServer: nginx
  ```

3. **Initialize EB**:

```
eb init -p python-3.9 recruitment-ai --region us-east-1
eb create recruitment-ai-env
```

Note: Ensure you have necessary permissions to interact with AWS Elastic Beanstalk

4. **Set Environment Variables** (optional):

```
   eb setenv AWS_ACCESS_KEY_ID=your_key AWS_SECRET_ACCESS_KEY=your_secret
```

Alternatively, use IAM roles for Bedrock access.

5. **Deploy**:

```
eb deploy
```

Access the app at the provided URL (e.g., `recruitment-ai-env.us-east-1.elasticbeanstalk.com`).

## CI/CD with GitHub Actions

To automate deployment:

1. **Workflow File**: Create `.github/workflows/deploy.yml`:

```
name: Deploy to AWS Elastic Beanstalk

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Install EB CLI
        run: pip install awsebcli --upgrade

      - name: Verify AWS credentials
        run: aws sts get-caller-identity

      - name: List Elastic Beanstalk environments
        run: aws elasticbeanstalk describe-environments --application-name recruitment-ai

      - name: Deploy to Elastic Beanstalk
        run: |
          eb init recruitment-ai -p python-3.9 --region us-east-1
          eb use recruitment-ai-env
          eb deploy recruitment-ai-env
```

2. **Secrets**: Add `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in GitHub repo Settings > Secrets and variables > Actions.

## Demo

- **Local**: Run locally and test all agents via the UI at `http://localhost:5000`.
- **Live**: http://recruitment-ai-env.eba-2ndqjfk6.us-east-1.elasticbeanstalk.com

## Dependencies

See `requirements.txt` for full list. Key dependencies:

- Flask: Web framework
- Flask-Cors: Cross-origin support
- boto3: AWS SDK for Bedrock
- gunicorn: WSGI server for EB

## Notes

- **Python Version**: Tested with Python 3.13.2 locally; EB deployment uses 3.9 due to platform support.
- **Security**: For production, secure AWS credentials via IAM roles or Secrets Manager instead of env vars.
- **Scalability**: Add error retries or caching for Bedrock calls in a production environment.
