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
                    },
                    "required": ["task_title", "module", "tip"],
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
                    "You are a study coach. Generate short, practical study tips for each task. "
                    "Use the task description and module context. "
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

    data = response.output_parsed
    return data["tips"]


