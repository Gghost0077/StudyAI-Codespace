from datetime import datetime, timedelta, date # for handling date and time




# Mapping of weekday numbers to their names
DAY_TO_WEEKDAY = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
}


#AI Additions for schedule generation - currently still being implemented and tested ( Currently a pplaceholder)
# trying ot return tasks ai_suggestions and explanations.

def apply_ai_personalisation(tasks, ai_enabled, ai_strictness):
  
    if not ai_enabled:
        return tasks, [], []

    suggestions = []
    explanations = []

    # Example behaviour:
    # If strictness is high, slightly increase importance for near-deadline tasks.
    today = datetime.now().date()

    for t in tasks:
        days_to_deadline = (t["deadline"] - today).days

        if ai_strictness == "high" and days_to_deadline <= 3:
            old = t["importance"]
            t["importance"] = min(3, old + 1)

            msg = f'Increased priority for "{t["title"]}" because deadline is in {days_to_deadline} days.'
            suggestions.append({
                "task_title": t["title"],
                "priority_delta": t["importance"] - old,
                "explanation": msg
            })
            explanations.append(msg)

        elif ai_strictness == "medium" and days_to_deadline <= 2:
            msg = f'Consider starting "{t["title"]}" earlier (deadline in {days_to_deadline} days).'
            suggestions.append({
                "task_title": t["title"],
                "priority_delta": 0,
                "explanation": msg
            })
            explanations.append(msg)

    return tasks, suggestions, explanations


# Math tools allowing us to convert between time formats and do calculations for the scheduler logic
def time_to_minutes(t: str) -> int:
    """Convert 'HH:MM' -> minutes since midnight (e.g. '08:30' -> 510)"""
    h, m = t.split(':')
    return int(h) * 60 + int(m)


def minutes_to_time(m: int) -> str:
    """Convert minutes since midnight -> 'HH:MM' (e.g. 510 -> '08:30')"""
    h = m // 60
    m = m % 60
    return f"{h:02d}:{m:02d}"

def parse_deadline(d: str) -> date:
    """Parse a deadline string in the format 'YYYY-MM-DD' and return a date object."""
    return datetime.strptime(d, "%Y-%m-%d").date()


# this flattens tasks all in one list allowing the scheduler to easily sort and prioritize them based on their deadlines and 
# importance. It also converts the estimated hours into minutes for easier scheduling calculations.
def flatten_and_sort_tasks(modules):

    tasks = []
    for m in modules:
        module_name =  (m.get("name") or "").strip()
        importance = int(m.get("importance", 2))

        for t in m.get("tasks", []):
            deadline_str  = t.get("deadline")
            if not deadline_str:
                continue  # Skip tasks without a deadline

            tasks.append({
                "module": module_name,
                "importance": importance,
                "title": (t.get("title") or "").strip(),
                "description": (t.get("description") or "").strip(),
                "deadline": parse_deadline(deadline_str),
                "minutes_needed": int(float(t.get("estimated_hours", 0)) * 60),
            })
    # Sort tasks by deadline, then by importance (descending)
    tasks.sort(key=lambda x: (x["deadline"], -x["importance"]))
    return tasks


def build_weekly_availability(availability):
    weekly = {i: [] for i in range(7)}

    for slot in availability:
        day = slot.get("day")
        wd = DAY_TO_WEEKDAY.get(day)

        if wd is None:
            continue

        start = slot.get("start")
        end = slot.get("end")

        if not start or not end:
            continue

        s = time_to_minutes(start)
        e = time_to_minutes(end)

        if s < e:
            weekly[wd].append((s, e))

    # Sort intervals for each day
    for wd in weekly:
        weekly[wd].sort()

    return weekly

def build_free_calendar(today, last_day, weekly):

    free = {}
    d = today 
    while d <= last_day:
        free[d] = weekly.get(d.weekday(), []).copy()  # Start with weekly availability for that day
        d += timedelta(days=1)
    return free

def generate_schedule(modules, availability, ai_enabled=False, ai_strictness="medium", chunk_minutes=60):
    tasks = flatten_and_sort_tasks(modules)
    if not tasks:
        return {"ai_used": bool(ai_enabled), 
                "sessions": [], 
                "warnings": ["No valid tasks with deadlines found."],
                "ai_suggestions": [],
                "ai_explanations": []
                }
    
    tasks, ai_suggestions, ai_explanations = apply_ai_personalisation(
        tasks, bool(ai_enabled), ai_strictness
    )

    # Re sorts after AI adjustments (if importance changed)
    tasks.sort(key=lambda x: (x["deadline"], -x["importance"]))
    
    weekly = build_weekly_availability(availability)

    print("Weekly keys:", list(weekly.keys()), flush=True)
    print("Weekly Monday entry (0):", weekly.get(0), flush=True)
    print("Weekly Tuesday entry (1):", weekly.get(1), flush=True)
    print("Weekly Wednesday entry (2):", weekly.get(2), flush=True)

    today = datetime.now().date()
    last_day = max(t["deadline"] for t in tasks)
    free = build_free_calendar(today, last_day, weekly) 
    sessions = []
    warnings = []

    for task in tasks:
        remaining = task["minutes_needed"]
        if remaining <= 0:
            continue

        d = today 
        while d <= task["deadline"] and remaining > 0:
            intervals = free.get(d, [])
            if not intervals:
                d += timedelta(days=1)
                continue

            new_intervals = []
            for (s, e) in intervals:
                cursor = s
                while cursor < e and remaining > 0:
                    alloc = min(chunk_minutes, remaining, e - cursor, remaining)
                    start_time = minutes_to_time(cursor)
                    end_time = minutes_to_time(cursor + alloc)
                    
                    sessions.append({
                        "module": task["module"],
                        "title": task["title"],
                        "date": d.isoformat(),
                        "start": start_time,
                        "end": end_time,
                        "minutes": alloc,
                        "source": "rule-based",
                        "note": f"scheduled before deadline {task['deadline'].isoformat()}",
                    })

                    cursor += alloc
                    remaining -= alloc
                if cursor < e:
                    new_intervals.append((cursor, e))
            free[d] = new_intervals
            d += timedelta(days=1)
        if remaining > 0:
            warnings.append(f"not enough time to fully schedule '{task['title']}' (missing {remaining}) minutes")

    return {"ai_used": bool(ai_enabled), 
            "sessions": sessions, 
            "warnings": warnings,
            "ai_suggestions": ai_suggestions,
            "ai_explanations": ai_explanations,
            "ai_strictness": ai_strictness
            }

    
    


