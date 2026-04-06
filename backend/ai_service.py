import json
import os 
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


#Generates study tips from task titles/descriptions of tasks using open AI
def get_study_tips_openai(tasks, strictness="medium"):
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not set")

    task_payload = [
        {
            "task_title": t.get("title", ""),
            "module": t.get("module", ""),
            "description": t.get("description", ""),
            "task_type": t.get("task_type", ""),
            "current_progress": t.get("current_progress", ""),
            "biggest_difficulty": t.get("biggest_difficulty", ""),
            "goal": t.get("goal", ""),
            "deadline": str(t.get("deadline", "")),
            "minutes_needed": t.get("minutes_needed", 0),
        }
        for t in tasks
    ]

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

    response = client.responses.create(
        model="gpt-5.4",
        input=[
            {
                "role": "system",
                "content": (

            "You are an academic study coach helping students follow a generated study schedule. "
            "For EACH task, return practical and specific guidance based on the task title, module, description, "
            "task type, current progress, biggest difficulty, goal, deadline, and minutes needed. "
            "Use the additional context fields when they are available. "
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
                "role": "user",
                "content": (
                    f"Strictness: {strictness}\n"
                    f"Tasks: {task_payload}"
                ),
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "study_tips",
                "schema": schema,
                "strict": True,
            }
        },
    )

# makes sure all fields are present and non-empty, with fallbacks if necessary
    raw_text = response.output[0].content[0].text
    data = json.loads(raw_text)
    tips = data["tips"]

    def safe_text(value, fallback):
        if isinstance(value, str) and value.strip():
            return value.strip()
        return fallback

    cleaned = []
    for t in tips:
        task_title = safe_text(t.get("task_title"), "Task")
        module = safe_text(t.get("module"), "Module")
        tip = safe_text(
            t.get("tip"),
            "Break this task into smaller chunks and complete one clear piece at a time.",
        )
        next_step = safe_text(
            t.get("next_step"),
            "Start by outlining the first small part of this task.",
        )
        session_focus = safe_text(
            t.get("session_focus"),
            "Complete one focused section of the task.",
        )

        progression_blocks = t.get("progression_blocks")
        if not isinstance(progression_blocks, list) or len(progression_blocks) == 0:
            progression_blocks = [
                "Understand the task requirements",
                "Start the first section",
                "Complete the main work",
                "Review and improve the result",
            ]
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

        cleaned.append({
            "task_title": task_title,
            "module": module,
            "tip": tip,
            "next_step": next_step,
            "progression_blocks": progression_blocks,
            "session_focus": session_focus,
        })

    return cleaned