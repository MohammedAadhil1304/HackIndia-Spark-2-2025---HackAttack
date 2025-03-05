from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize the database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  crime_type TEXT NOT NULL,
                  description TEXT NOT NULL,
                  date_reported TEXT NOT NULL,
                  status TEXT DEFAULT 'Pending')''')
    conn.commit()
    conn.close()

init_db()

# Home Page
@app.route('/')
def home():
    return render_template('home.html')

# Report Crime Page
@app.route('/report')
def report():
    return render_template('report.html')

# Chatbot Endpoint for Reporting with Gemini
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message'].lower()
    conversation_state = request.json.get('conversation_state', {})

    # Define a prompt for Gemini to handle crime reporting step-by-step
    prompt = f"""
    You are CyberShieldAI, an assistant designed to help users report cybercrimes through conversation.
    The user said: "{user_input}".
    Current conversation state: {json.dumps(conversation_state)}.
    Your goals:
    1. Collect the crime type (e.g., phishing, hacking, identity theft).
    2. Collect a detailed description of the incident.
    3. Collect the date of the incident (in YYYY-MM-DD format).
    Rules:
    - Ask only ONE question at a time, based on what’s missing from the conversation state.
    - If the user’s input provides a piece of information, update the conversation state and move to the next missing piece.
    - Do NOT ask multiple questions in a single response.
    - If all details (crime_type, description, date_reported) are collected, return a JSON response with the report data and a message suggesting submission.
    - If the input is unclear, ask for clarification about the current step only.
    Response format:
    - For questions: Plain text with one question.
    - When all details are collected:
    {{
        "message": "Here’s the report I’ve prepared:\\nCrime Type: [crime_type]\\nDescription: [description]\\nDate: [date_reported]\\nReady to submit?",
        "report": {{ "crime_type": "...", "description": "...", "date_reported": "..." }},
        "ready_to_submit": true
    }}
    Current date for reference: 2025-03-05 (use this to interpret relative dates like 'yesterday').
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Check if Gemini returned a JSON response
        if response_text.startswith('{') and response_text.endswith('}'):
            return jsonify(json.loads(response_text))
        else:
            return jsonify({
                "message": response_text,
                "report": conversation_state,
                "ready_to_submit": False
            })
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}. Please try again.", "report": {}, "ready_to_submit": False})

# Submit Report from Chat
@app.route('/submit_report', methods=['POST'])
def submit_report():
    report_data = request.json
    crime_type = report_data.get('crime_type')
    description = report_data.get('description')
    date_reported = report_data.get('date_reported')

    if not all([crime_type, description, date_reported]):
        return jsonify({"success": False, "message": "Incomplete report data."})

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO reports (crime_type, description, date_reported) VALUES (?, ?, ?)",
              (crime_type, description, date_reported))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Report submitted successfully!"})

# AI Awareness Endpoint with Gemini
@app.route('/ai-awareness', methods=['POST'])
def ai_awareness():
    user_input = request.json['message'].lower()
    
    prompt = f"""
    You are a Cybersecurity Awareness AI designed to educate users about staying safe online.
    The user asked: "{user_input}".
    Provide a clear, educational response about cybersecurity topics (e.g., phishing, passwords, 2FA, hacking prevention).
    If the input is unclear, ask for clarification or suggest common topics.
    """
    
    try:
        response = model.generate_content(prompt)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}. Please try again."})

# Awareness Page
@app.route('/awareness')
def awareness():
    return render_template('awareness.html')

# Dashboard Page
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM reports")
    reports = c.fetchall()
    conn.close()
    return render_template('dashboard.html', reports=reports)

if __name__ == '__main__':
    app.run(debug=True)