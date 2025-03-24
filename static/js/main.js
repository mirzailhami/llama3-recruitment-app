// main.js
async function fetchJson(url, options = {}) {
  const res = await fetch(url, options);
  return await res.json();
}

function showOutput(elementId, content) {
  const output = document.getElementById(elementId);
  output.value = content;
  output.classList.remove("hidden");
}

function clearOutput(elementId) {
  const output = document.getElementById(elementId);
  output.value = "";
  output.classList.add("hidden");
}

// Sample Data Generators
document
  .getElementById("gen-requirements")
  .addEventListener("click", async () => {
    const data = await fetchJson("/generate_requirements");
    document.getElementById("job_title").value = data.job_title;
    document.getElementById("skills").value = data.skills.join(", ");
    document.getElementById("experience_level").value = data.experience_level;
  });

document.getElementById("gen-resumes").addEventListener("click", async () => {
  try {
    // Get the job description from jd-output
    const job_description = document.getElementById("jd-output").value;

    if (!job_description) {
      alert("Please generate a job description first in the JD Generator section.");
      return;
    }

    // Send POST request to /generate_resumes with job_description
    const data = await fetchJson("/generate_resumes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ job_description }),
    });

    const resumes = data.resumes || data.error;
    document.getElementById("resumes").value = JSON.stringify(resumes, null, 2);
  } catch (error) {
    console.error("Error generating resumes:", error);
    alert("An error occurred while generating resumes. Check the console.");
  }
});

document
  .getElementById("gen-sample-transcript")
  .addEventListener("click", async () => {
    try {
      // Get the ranked resumes from the textarea
      const rankedResumesText = document.getElementById("resume-output").value;
      const job_description = document.getElementById("jd-output").value;
      const chat_transcript = document.getElementById("chat-box").innerText || null;

      // Default top candidate
      let topCandidate = "John Doe";

      // Parse the ranked resumes JSON and extract the top candidate
      if (rankedResumesText) {
        const rankedResumes = JSON.parse(rankedResumesText);
        if (Array.isArray(rankedResumes) && rankedResumes.length > 0) {
          topCandidate = rankedResumes[0].name || topCandidate;
        }
      }

      // Validate job description
      if (!job_description) {
        return showOutput(
          "sentiment-output",
          "Please generate a job description first."
        );
      }

      // Send the data to the /generate_sample_transcript endpoint
      const data = await fetchJson("/generate_sample_transcript", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          top_candidate: topCandidate,
          job_description,
          chat_transcript,
        }),
      });

      // Display the generated transcript or error message
      document.getElementById("interview_transcript_sentiment").value =
        data.transcript || data.error;

      // Clear the sentiment output
      clearOutput("sentiment-output");
    } catch (error) {
      console.error("Error generating sample transcript:", error);
      showOutput("sentiment-output", "An error occurred. Please check the console.");
    }
  });

// JD Generator
document.getElementById("jd-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const job_title = document.getElementById("job_title").value;
  const skills = document
    .getElementById("skills")
    .value.split(",")
    .map((s) => s.trim());
  const experience_level = document.getElementById("experience_level").value;

  const data = await fetchJson("/generate_jd", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_title, skills, experience_level }),
  });
  showOutput("jd-output", data.job_description || data.error);
  document.getElementById("job_description").value = data.job_description;
  document.getElementById("interview_job_description").value =
    data.job_description;
});

// ResumeRanker
document.getElementById('resume-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    // Get the job description and resumes from the textareas
    const job_description = document.getElementById('job_description').value;
    const resumes = document.getElementById('resumes').value;

    if (!job_description || !resumes) {
        alert('Please provide both a job description and resumes.');
        return;
    }

    try {
        // Parse the resumes from the textarea into a JSON array
        const resumesArray = JSON.parse(resumes);

        // Validate that resumesArray is a list of objects
        if (!Array.isArray(resumesArray) || !resumesArray.every(r => typeof r === 'object' && r !== null)) {
            throw new Error("Resumes must be a valid JSON array of objects.");
        }

        // Send the data to the /rank_resumes endpoint
        const data = await fetchJson('/rank_resumes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_description, resumes: resumesArray })
        });

        // Sort the ranked_resumes and display in the output textarea
        data.ranked_resumes = data.ranked_resumes.sort((a,b) => b.score - a.score);
        document.getElementById('resume-output').value = JSON.stringify(data.ranked_resumes, null, 2);
        document.getElementById('resume-output').classList.remove('hidden');

        // Update the schedule inputs after ranking resumes
        updateScheduleInputs();
    } catch (error) {
        console.error('Error ranking resumes:', error);
        alert('An error occurred while ranking resumes. Please check the console for details.');
    }
});

// Email Automation
document.getElementById("send-emails").addEventListener("click", async () => {
  try {
    // Get the ranked resumes and job description
    const rankedResumes = JSON.parse(
      document.getElementById("resume-output").value
    );
    const jobDescription = document.getElementById("job_description").value;

    if (!rankedResumes || !jobDescription) {
      alert("Please rank resumes and provide a job description first.");
      return;
    }

    // Send the data to the /automate_email endpoint
    const data = await fetchJson("/automate_email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ranked_resumes: rankedResumes,
        job_description: jobDescription,
      }),
    });

    // Display the email responses in the output textarea
    document.getElementById("email-output").value = JSON.stringify(
      data,
      null,
      2
    );
    document.getElementById("email-output").classList.remove("hidden");
  } catch (error) {
    console.error("Error sending emails:", error);
    alert(
      "An error occurred while sending emails. Please check the console for details."
    );
  }
});

// InterviewScheduler
document.getElementById('schedule-interviews').addEventListener('click', async () => {
  try {
      // Get the ranked resumes from the textarea
      const rankedResumesText = document.getElementById('resume-output').value;

      if (!rankedResumesText) {
          alert('Please rank resumes first.');
          return;
      }

      // Parse the ranked resumes as JSON
      const rankedResumes = JSON.parse(rankedResumesText);

      // Collect the interview times
      const interviewTimes = [];
      rankedResumes.forEach((_, index) => {
          const timeInput = document.getElementById(`interview_time_${index}`);
          if (timeInput && timeInput.value) {
              interviewTimes.push(timeInput.value);
          }
      });

      // Disabled: Backend can handle empty interviewTimes with AI-generated times
      // if (interviewTimes.length === 0) {
      //     alert('Please set at least one interview time.');
      //     return;
      // }

      // Send the data to the /schedule_interview endpoint
      const data = await fetchJson('/schedule_interview', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ranked_resumes: rankedResumes, interview_times: interviewTimes })
      });

      // Display the schedule confirmations in the output textarea
      document.getElementById('schedule-output').value = JSON.stringify(data, null, 2);
      document.getElementById('schedule-output').classList.remove('hidden');
  } catch (error) {
      console.error('Error scheduling interviews:', error);
      alert('An error occurred while scheduling interviews. Please check the console for details.');
  }
});

// InterviewAgent
document
  .getElementById("interview-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const job_description = document.getElementById(
      "interview_job_description"
    ).value;
    const candidate_response =
      document.getElementById("candidate_response").value || null;
    const chatBox = document.getElementById("chat-box");

    if (!job_description) {
      chatBox.innerHTML =
        '<p class="text-red-500">Please provide a job description.</p>';
      return;
    }

    const data = await fetchJson("/conduct_interview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ job_description, candidate_response }),
    });

    if (data.question) {
      chatBox.innerHTML = candidate_response
        ? `${chatBox.innerHTML}<p class="mb-2"><strong>You:</strong> ${candidate_response}</p><p class="mb-2"><strong>AI:</strong> ${data.question}</p>`
        : `<p class="mb-2"><strong>AI:</strong> ${data.question}</p>`;
      document.getElementById("candidate_response").value = "";
    } else {
      chatBox.innerHTML += `<p class="text-red-500">${data.error}</p>`;
    }
    chatBox.scrollTop = chatBox.scrollHeight;
  });

document.getElementById("clear-chat").addEventListener("click", () => {
  document.getElementById("chat-box").innerHTML = "";
  document.getElementById("candidate_response").value = "";
});

// HireRecommendationAgent
document.getElementById("hire-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const chatBox = document.getElementById("chat-box").innerText;
  const interview_transcript =
    chatBox || document.getElementById("interview_transcript_hire").value;

  if (!interview_transcript)
    return showOutput("hire-output", "Please provide an interview transcript.");

  const data = await fetchJson("/recommend_hire", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ interview_transcript }),
  });
  showOutput(
    "hire-output",
    data.recommendation || data.error || "No recommendation returned."
  );
  document.getElementById("interview_transcript_sentiment").value =
    interview_transcript;
});

document.getElementById("load-transcript").addEventListener("click", () => {
  const chatBox = document.getElementById("chat-box").innerText;
  if (chatBox) {
    document.getElementById("interview_transcript_hire").value = chatBox;
  } else {
    showOutput("hire-output", "No chat transcript available.");
  }
});

// SentimentAnalyzer
document
  .getElementById("sentiment-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const interview_transcript = document.getElementById(
      "interview_transcript_sentiment"
    ).value;

    if (!interview_transcript)
      return showOutput(
        "sentiment-output",
        "Please provide an interview transcript."
      );

    const data = await fetchJson("/analyze_sentiment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ interview_transcript }),
    });
    showOutput(
      "sentiment-output",
      data.sentiment || data.error || "No sentiment analysis returned."
    );
  });

  function updateScheduleInputs() {
    // Get the ranked resumes from the textarea
    const rankedResumesText = document.getElementById('resume-output').value;
    const scheduleInputs = document.getElementById('schedule-inputs');
    scheduleInputs.innerHTML = ''; // Clear previous inputs

    if (!rankedResumesText) {
        scheduleInputs.innerHTML = '<p>Please rank resumes first.</p>';
        return;
    }

    try {
        // Parse the ranked resumes as JSON
        const rankedResumes = JSON.parse(rankedResumesText);

        // Generate input fields for each candidate
        rankedResumes.forEach((resume, index) => {
            const name = resume.name || "Unknown Candidate";
            const email = resume.email || `${name.toLowerCase().replace(' ', '.')}@example.com`;

            // Create a new input field for each candidate
            const inputDiv = document.createElement('div');
            inputDiv.className = 'mb-2';
            inputDiv.innerHTML = `
                <label class="block">${name} (${email}):</label>
                <input type="datetime-local" id="interview_time_${index}" class="border p-2 w-full">
            `;
            scheduleInputs.appendChild(inputDiv);
        });
    } catch (error) {
        console.error('Error parsing ranked resumes:', error);
        scheduleInputs.innerHTML = '<p>Invalid ranked resumes format.</p>';
    }
}