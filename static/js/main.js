// main.js
async function fetchJson(url, options = {}) {
    const res = await fetch(url, options);
    return await res.json();
}

function showOutput(elementId, content) {
    const output = document.getElementById(elementId);
    output.value = content;
    output.classList.remove('hidden');
}

function clearOutput(elementId) {
    const output = document.getElementById(elementId);
    output.value = '';
    output.classList.add('hidden');
}

// Sample Data Generators
document.getElementById('gen-requirements').addEventListener('click', async () => {
    const data = await fetchJson('/generate_requirements');
    document.getElementById('job_title').value = data.job_title;
    document.getElementById('skills').value = data.skills.join(', ');
    document.getElementById('experience_level').value = data.experience_level;
});

document.getElementById('gen-resumes').addEventListener('click', async () => {
    const data = await fetchJson('/generate_resumes');
    document.getElementById('resumes').value = data.resumes.join('\n');
});

document.getElementById('gen-sample-transcript').addEventListener('click', async () => {
    const rankedResumes = document.getElementById('resume-output').textContent;
    const job_description = document.getElementById('jd-output').textContent;
    const chat_transcript = document.getElementById('chat-box').innerText || null;
    let topCandidate = 'John Doe';
    if (rankedResumes) {
        const lines = rankedResumes.split('\n').filter(l => l.trim());
        topCandidate = lines[0]?.split(':')[0].replace('-', '').trim() || topCandidate;
    }
    if (!job_description) return showOutput('sentiment-output', 'Please generate a job description first.');

    const data = await fetchJson('/generate_sample_transcript', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ top_candidate: topCandidate, job_description, chat_transcript })
    });
    document.getElementById('interview_transcript_sentiment').value = data.transcript || data.error;
    clearOutput('sentiment-output');
});

// JD Generator
document.getElementById('jd-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const job_title = document.getElementById('job_title').value;
    const skills = document.getElementById('skills').value.split(',').map(s => s.trim());
    const experience_level = document.getElementById('experience_level').value;

    const data = await fetchJson('/generate_jd', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_title, skills, experience_level })
    });
    showOutput('jd-output', data.job_description || data.error);
    document.getElementById('job_description').value = data.job_description;
    document.getElementById('interview_job_description').value = data.job_description;
});

// ResumeRanker
document.getElementById('resume-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const job_description = document.getElementById('job_description').value;
    const resumes = document.getElementById('resumes').value.split('\n').filter(r => r.trim());

    if (!job_description || !resumes.length) return showOutput('resume-output', 'Please provide both a job description and resumes.');

    const data = await fetchJson('/rank_resumes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_description, resumes })
    });
    showOutput('resume-output', data.ranked_resumes || data.error);
    updateScheduleInputs();
});

// Email Automation
document.getElementById('send-emails').addEventListener('click', async () => {
    const ranked_resumes = document.getElementById('resume-output').textContent;
    const job_description = document.getElementById('jd-output').textContent;

    if (!ranked_resumes || !job_description) return showOutput('email-output', 'Please generate a job description and rank resumes first.');

    const data = await fetchJson('/automate_email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ranked_resumes, job_description })
    });
    showOutput('email-output', Array.isArray(data) ? JSON.stringify(data, null, 2) : data.error);
});

// InterviewScheduler
document.getElementById('schedule-interviews').addEventListener('click', async () => {
    const ranked_resumes = document.getElementById('resume-output').textContent;
    if (!ranked_resumes || ranked_resumes === 'python') return showOutput('schedule-output', 'Please rank resumes correctly first.');

    const resumes = ranked_resumes.split('\n').filter(r => r.trim());
    const interview_times = resumes.map((_, i) => document.getElementById(`interview_time_${i}`).value).filter(Boolean);

    if (!interview_times.length) return showOutput('schedule-output', 'Please set at least one interview time.');

    const data = await fetchJson('/schedule_interview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ranked_resumes, interview_times })
    });
    showOutput('schedule-output', Array.isArray(data) ? JSON.stringify(data, null, 2) : data.error);
});

// InterviewAgent
document.getElementById('interview-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const job_description = document.getElementById('interview_job_description').value;
    const candidate_response = document.getElementById('candidate_response').value || null;
    const chatBox = document.getElementById('chat-box');

    if (!job_description) {
        chatBox.innerHTML = '<p class="text-red-500">Please provide a job description.</p>';
        return;
    }

    const data = await fetchJson('/conduct_interview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_description, candidate_response })
    });

    if (data.question) {
        chatBox.innerHTML = candidate_response
            ? `${chatBox.innerHTML}<p class="mb-2"><strong>You:</strong> ${candidate_response}</p><p class="mb-2"><strong>AI:</strong> ${data.question}</p>`
            : `<p class="mb-2"><strong>AI:</strong> ${data.question}</p>`;
        document.getElementById('candidate_response').value = '';
    } else {
        chatBox.innerHTML += `<p class="text-red-500">${data.error}</p>`;
    }
    chatBox.scrollTop = chatBox.scrollHeight;
});

document.getElementById('clear-chat').addEventListener('click', () => {
    document.getElementById('chat-box').innerHTML = '';
    document.getElementById('candidate_response').value = '';
});

// HireRecommendationAgent
document.getElementById('hire-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const chatBox = document.getElementById('chat-box').innerText;
    const interview_transcript = chatBox || document.getElementById('interview_transcript_hire').value;

    if (!interview_transcript) return showOutput('hire-output', 'Please provide an interview transcript.');

    const data = await fetchJson('/recommend_hire', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ interview_transcript })
    });
    showOutput('hire-output', data.recommendation || data.error || 'No recommendation returned.');
    document.getElementById('interview_transcript_sentiment').value = interview_transcript;
});

document.getElementById('load-transcript').addEventListener('click', () => {
    const chatBox = document.getElementById('chat-box').innerText;
    if (chatBox) {
        document.getElementById('interview_transcript_hire').value = chatBox;
    } else {
        showOutput('hire-output', 'No chat transcript available.');
    }
});

// SentimentAnalyzer
document.getElementById('sentiment-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const interview_transcript = document.getElementById('interview_transcript_sentiment').value;

    if (!interview_transcript) return showOutput('sentiment-output', 'Please provide an interview transcript.');

    const data = await fetchJson('/analyze_sentiment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ interview_transcript })
    });
    showOutput('sentiment-output', data.sentiment || data.error || 'No sentiment analysis returned.');
});

function updateScheduleInputs() {
    const ranked_resumes = document.getElementById('resume-output').textContent;
    const scheduleInputs = document.getElementById('schedule-inputs');
    scheduleInputs.innerHTML = '';

    if (!ranked_resumes || ranked_resumes === 'python') {
        scheduleInputs.innerHTML = '<p>Please rank resumes correctly first.</p>';
        return;
    }

    const resumes = ranked_resumes.split('\n').filter(r => r.trim());
    resumes.forEach((resume, index) => {
        const name = resume.split(':')[0].replace('-', '').trim();
        const email = resume.split('email:')?.[1]?.trim() || `${name.toLowerCase().replace(' ', '.')}@example.com`;
        scheduleInputs.innerHTML += `
            <div class="mb-2">
                <label class="block">${name} (${email}):</label>
                <input type="datetime-local" id="interview_time_${index}" class="border p-2 w-full">
            </div>
        `;
    });
}