from datetime import datetime

def generate_schedule(modules, availability, ai_enabled = False):
    """
    The basic rule based scheduler:
    - sort tasks by deadline
    - allocate study blocks based on availability
    """

    all_tasks = []
    for module in modules:
        for task in module['tasks']:
            all_tasks.append({
                "module": module['name'],
                "title": task['title'],
                "deadline": task['deadline'],
                "hours": task['estimated_hours']
            })
    # Sort tasks by deadline
    all_tasks.sort(key=lambda x: x['deadline'])

    scheduled_sessions = []
    for task in all_tasks:
        scheduled_sessions.append({
            "module": task['module'],
            "title": task['title'],
            "allocated_hours": task['hours'],
            "note": "Scheduled using basic rule-based scheduler"
        })

    return {
        "sessions": scheduled_sessions,
        "ai_used": ai_enabled
    }