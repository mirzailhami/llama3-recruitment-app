# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
from agents import (generate_hiring_requirements, generate_resumes, generate_jd, rank_resumes,
                   automate_email, schedule_interview, conduct_interview, recommend_hire,
                   generate_sample_transcript, analyze_sentiment)
from utils import call_llama3

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Server is alive!'})

@app.route('/generate_requirements', methods=['GET'])
def generate_requirements_endpoint():
    try:
        requirements = generate_hiring_requirements()
        return jsonify(requirements)
    except Exception as e:
        logging.error(f"Requirements generation error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/generate_resumes', methods=['POST'])
def generate_resumes_endpoint():
    try:
        data = request.get_json() or {}
        job_description = data.get('job_description', '# Generic Job\nSkills: Python, Java\nExperience: Mid')
        resumes = generate_resumes(job_description)
        return jsonify({'resumes': resumes})
    except Exception as e:
        logging.error(f"Resume generation error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/generate_jd', methods=['POST'])
def generate_jd_endpoint():
    try:
        data = request.get_json()
        job_title = data.get('job_title', '')
        skills = data.get('skills', [])
        experience_level = data.get('experience_level', 'Entry')
        if not job_title or not skills:
            return jsonify({'error': 'Missing job_title or skills'}), 400
        jd_text = generate_jd(job_title, skills, experience_level)
        return jsonify({'job_description': jd_text})
    except Exception as e:
        logging.error(f"JD error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/rank_resumes', methods=['POST'])
def rank_resumes_endpoint():
    try:
        data = request.get_json()
        job_description = data.get('job_description', '')
        resumes = data.get('resumes', [])

        if not job_description or not resumes:
            return jsonify({'error': 'Missing job_description or resumes'}), 400

        # Call the rank_resumes function
        ranked_resumes = rank_resumes(job_description, resumes)
        return jsonify({'ranked_resumes': ranked_resumes})
    except Exception as e:
        logging.error(f"Rank resumes error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500
    
@app.route('/automate_email', methods=['POST'])
def automate_email_endpoint():
    try:
        data = request.get_json()
        ranked_resumes = data.get('ranked_resumes', [])
        job_description = data.get('job_description', '')

        if not ranked_resumes or not job_description:
            return jsonify({'error': 'Missing ranked_resumes or job_description'}), 400

        # Call the automate_email function
        emails = automate_email(ranked_resumes, job_description)
        return jsonify(emails)
    except Exception as e:
        logging.error(f"Email automation error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/schedule_interview', methods=['POST'])
def schedule_interview_endpoint():
    try:
        data = request.get_json()
        ranked_resumes = data.get('ranked_resumes', [])
        interview_times = data.get('interview_times', [])

        # if not ranked_resumes or not interview_times:
        #     return jsonify({'error': 'Missing ranked_resumes or interview_times'}), 400

        # Call the schedule_interview function
        confirmations = schedule_interview(ranked_resumes, interview_times)
        return jsonify(confirmations)
    except Exception as e:
        logging.error(f"Scheduling error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/conduct_interview', methods=['POST'])
def conduct_interview_endpoint():
    try:
        data = request.get_json()
        job_description = data.get('job_description', '')
        candidate_response = data.get('candidate_response', None)
        if not job_description:
            return jsonify({'error': 'Missing job_description'}), 400
        question = conduct_interview(job_description, candidate_response)
        return jsonify({'question': question})
    except Exception as e:
        logging.error(f"Interview error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/recommend_hire', methods=['POST'])
def recommend_hire_endpoint():
    try:
        data = request.get_json()
        interview_transcript = data.get('interview_transcript', '')
        if not interview_transcript:
            return jsonify({'error': 'Missing interview_transcript'}), 400
        recommendation = recommend_hire(interview_transcript)
        return jsonify({'recommendation': recommendation})
    except Exception as e:
        logging.error(f"Hire recommendation error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/generate_sample_transcript', methods=['POST'])
def generate_sample_transcript_endpoint():
    try:
        data = request.get_json()
        top_candidate = data.get('top_candidate', '')
        job_description = data.get('job_description', '')
        chat_transcript = data.get('chat_transcript', None)
        if not top_candidate or not job_description:
            return jsonify({'error': 'Missing top_candidate or job_description'}), 400
        transcript = generate_sample_transcript(top_candidate, job_description, chat_transcript)
        return jsonify({'transcript': transcript})
    except Exception as e:
        logging.error(f"Transcript error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/analyze_sentiment', methods=['POST'])
def analyze_sentiment_endpoint():
    try:
        data = request.get_json()
        interview_transcript = data.get('interview_transcript', '')
        if not interview_transcript:
            return jsonify({'error': 'Missing interview_transcript'}), 400
        sentiment = analyze_sentiment(interview_transcript)
        return jsonify({'sentiment': sentiment})
    except Exception as e:
        logging.error(f"Sentiment analysis error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)