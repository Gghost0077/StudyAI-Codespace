# StudyAI – AI-Powered Study Planner

A Flask web application that turns your module briefs into a personalised study schedule, using AI to generate tailored tips based on your tasks, deadlines, and progress.

## How It Works

1. Upload your module briefs as PDF or Word documents
2. The app extracts and processes the relevant task and deadline information
3. You provide details for each task — module, task type, current progress, biggest difficulty, and goals
4. The scheduler converts your weekly availability into time slots and builds a personalised study plan
5. AI (via the OpenAI API) generates study tips and priority suggestions, with adjustable "strictness" levels

## Features

- PDF/DOCX parsing for module briefs (PyPDF2, python-docx)
- Custom scheduling engine that maps tasks to available time slots
- AI-generated, schema-validated study tips tailored to each task
- Adjustable AI strictness for more or less assertive recommendations
- Logging of scheduling events for review

## Tech Stack

- Python, Flask, Flask-CORS
- OpenAI API for AI-generated tips
- PyPDF2 / python-docx for document parsing
- Gunicorn for deployment

## Project Structure

```
backend/
├── app.py            # Flask entry point – routes for uploads, scheduling, logging
├── scheduler.py       # Core scheduling logic and AI personalisation
├── ai_service.py       # OpenAI integration for generating study tips
├── requirements.txt
├── templates/
└── static/
```

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r backend/requirements.txt
   ```
3. Create a `.env` file in `backend/` with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_key_here
   ```
4. Run the app:
   ```
   python backend/app.py
   ```
