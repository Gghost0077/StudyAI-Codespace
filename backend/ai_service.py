# This files contains the AI related functions, such as generating study tips from task details using OpenAI's API.
# it takes the cleaned task list from the scheduler and sends it to the OpenAI API with a system prompt that instructs the model to act as an academic study coach.



# ========================
# Imports and Client Setup
# ========================


import json # used to parse the JSON response from the OpenAI API, ensuring that the data can be easily manipulated and returned in a structured format.
import os  # used to read environment variables, specifically to access the OpenAI API key securely without hardcoding it in the codebase.
from openai import OpenAI # imports the OpenAI client library, which provides the necessary functions to interact with the OpenAI API for generating responses based on the provided prompts and input data.


# creates the openAI client using the API key from the environment variable,
#  allowing the application to securely authenticate with the OpenAI API and make requests to generate study tips based on the task details.
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY")) 




# =======================
# Generate Study Tips Function
# =======================
def get_study_tips_openai(tasks, strictness="medium"):

    # checks whether the API key is set in the environment variables before making any API calls.
    #  If the key is missing, it raises a RuntimeError to alert the developer or user
    #  that the necessary configuration is not in place for the function to operate correctly.
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not set")

# builds a simplified AI-facing version of each task, extracting only the relevant fields needed for the AI to generate study tips.
    task_payload = [
        {
            "task_title": t.get("title", ""),
            "module": t.get("module", ""),
            "description": t.get("description", ""),
            "module_brief_text": t.get("module_brief_text", ""),
            "task_type": t.get("task_type", ""),
            "current_progress": t.get("current_progress", ""),
            "biggest_difficulty": t.get("biggest_difficulty", ""),
            "goal": t.get("goal", ""),
            "deadline": str(t.get("deadline", "")),
            "minutes_needed": t.get("minutes_needed", 0),
        }
        for t in tasks
    ]

# defines the expected JSON schema for the AI response, specifying the structure and types of the data that the AI should return.
# making sure the AI response adheres to this schema allows for consistent parsing and handling of the generated study tips,
#  ensuring that all necessary fields are present and correctly formatted for use in the frontend.
    schema = {
    "type": "object",
    "properties": {
        "tips": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "task_title": {"type": "string"},
                    "module": {"type": "string"},
                    "tip": {"type": "string"},
                    "next_step": {"type": "string"},
                    "progression_blocks": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "session_focus": {"type": "string"}
                },
                "required": [
                    "task_title",
                    "module",
                    "tip",
                    "next_step",
                    "progression_blocks",
                    "session_focus"
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["tips"],
    "additionalProperties": False,
}

# calls the OpenAI API to generate study tips based on the provided tasks and strictness level,
#  using a detailed system prompt to guide the AI's response.
    response = client.responses.create(
        model="gpt-5.4",
    
    # starts the prompt input list and begins the system message that instructs the AI on how to generate the study tips.
        input=[
            {
                "role": "system",
                "content": (

            "You are an academic study coach helping students follow a generated study schedule. "
            "For EACH task, return practical and specific guidance based on the task title, module, description, "
            "task type, current progress, biggest difficulty, goal, deadline, and minutes needed. "
            "Use the additional context fields when they are available. "
            "If module brief text is provided, use it to understand the assessment requirements, deliverables, "
            "and likely work stages before giving advice. "
            "Make the advice feel personalised to the student's current situation. "
            "Return all fields with meaningful content. Never leave any field empty. "
            "Do not use placeholders like 'No next step available'. "
            "Rules: "
            "1. tip: one short practical study tip tailored to the actual task and difficulty. "
            "2. next_step: one concrete action the student can start immediately, starting with a verb. "
            "3. progression_blocks: 3 to 5 short ordered stages showing how to complete the task over time. "
            "4. session_focus: one precise focus for the very next study session only. "
            "5. If current progress is 'Not started', make the next step small and easy to begin. "
            "6. If current progress is 'Half done' or 'Nearly finished', focus on completion and refinement. "
            "7. If biggest difficulty is given, directly address that difficulty in the advice. "
            "8. If a goal is provided, align the tip and next step with that goal. "
            "9. Keep each field concise, specific, and actionable. "
            "Return only valid JSON matching the schema."
            ),
            },
            {
            #sends the user message containing the strictness level and the task payload, 
            # which includes all the relevant details of the tasks that the AI will use to generate the study tips.
                "role": "user",
                "content": (
                    f"Strictness: {strictness}\n"
                    f"Tasks: {task_payload}"
                ),
            },
        ],
        # tells the OpenAI API to format the response according to the defined JSON schema, 
        # ensuring that the output can be reliably parsed and used by the frontend.
        text={
            "format": {
                "type": "json_schema",
                "name": "study_tips",
                "schema": schema,
                "strict": True,
            }
        },
    )



#=======================
# Parse and Clean AI Response
#=======================

# extrats the returned JSON text from the response object 
#parses the JSON text into a Python dictionary, 
# and then iterates through each tip to clean and validate the content,
#  ensuring that all fields are populated with meaningful information and applying fallbacks where necessary.
    raw_text = response.output[0].content[0].text
    data = json.loads(raw_text)
    tips = data["tips"]

# helper to ensure that each field in the AI response is a non-empty string, providing a fallback value if the field is missing or empty.
    def safe_text(value, fallback):
        if isinstance(value, str) and value.strip():
            return value.strip()
        return fallback

# starts the final output cleaning loop 
    cleaned = []
    for t in tips:
    # ensures that the task title and module fields are populated with the actual task title and module from the AI response,
    #  or default values if they are missing.
        task_title = safe_text(t.get("task_title"), "Task")
        module = safe_text(t.get("module"), "Module")
        # use the AI tip if valid 
        # otherwise, provide a generic fallback tip that encourages breaking the task into smaller chunks and focusing on one piece at a time.
        tip = safe_text(
            t.get("tip"),
            "Break this task into smaller chunks and complete one clear piece at a time.",
        )
        # same idea for the next step, ensuring that it is a specific action the student can take immediately,
        #  or a generic starting point if the AI did not provide one.
        next_step = safe_text(
            t.get("next_step"),
            "Start by outlining the first small part of this task.",
        )
        # same for the session focus, ensuring that it provides a clear and actionable focus for the next study session,
        #  or a general recommendation to focus on one section of the task if the AI did
        session_focus = safe_text(
            t.get("session_focus"),
            "Complete one focused section of the task.",
        )
# checks the progression blocks field to ensure it is a non-empty list of strings, 
# providing a default set of progression stages if the AI did not return valid content.
        progression_blocks = t.get("progression_blocks")
        if not isinstance(progression_blocks, list) or len(progression_blocks) == 0:
            progression_blocks = [
                "Understand the task requirements",
                "Start the first section",
                "Complete the main work",
                "Review and improve the result",
            ]
        # cleans each progression block into a non-empty string, 
        # and if all blocks are empty after cleaning, it falls back to the default progression stages.
        else:
            progression_blocks = [
                str(p).strip() for p in progression_blocks if str(p).strip()
            ]
            if len(progression_blocks) == 0:
                progression_blocks = [
                    "Understand the task requirements",
                    "Start the first section",
                    "Complete the main work",
                    "Review and improve the result",
                ]
# builds the final cleaned tip object with all the validated and cleaned fields, and appends it to the cleaned list that will be returned to the frontend.
        cleaned.append({
            "task_title": task_title,
            "module": module,
            "tip": tip,
            "next_step": next_step,
            "progression_blocks": progression_blocks,
            "session_focus": session_focus,
        })
# returns the list of cleaned tips, which will be used by the frontend to display personalized study advice to the user based on their tasks and the AI's analysis.
    return cleaned