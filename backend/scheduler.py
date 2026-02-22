from datetime import datetime, timedelta # for handling date and time

# Mapping of weekday numbers to their names
DAY_TO_WEEKDAY = {
    0: "Monday",
    1: "Tuesday", 
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}

# Math tools allowing us to convert between time formats and do calculations for the schdeuler logic
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


def build_weekly_avaliability(availability):
    
    weekly = {i: [] for i in range(7)}  # Initialize empty lists for each day of the week

    for slot in availability:
        wd = DAY_TO_WEEKDAY.get(slot.get("day"))
        if wd is None:
            continue

        start = slot.get("start")
        end = slot.get("end")
        if not start or not end:
            continue

        s = time_to_minutes(start)
        e = time_to_minutes(end)

        if s >= e:
            weekly[wd].append((s, e))
    for wd in weekly:
        weekly[wd].sort()  # Sort time slots for each day
    
    return weekly

def build_free_calendar(today, last_day, weekly):

    free = {}
    d = today 
    while d <= last_day:
        free[d] = weekly.get(d.weekday(), []).copy()  # Start with weekly availability for that day
        d += timedelta(days=1)
    return free

def generate_schedule(modules, availability, ai_enabled=False, chunk_minutes=60):
    tasks = flatten_and_sort_tasks(modules)
    if not tasks:
        return {"ai_used": bool(ai_enabled), "sessions": [], "warnings": ["No valid tasks with deadlines found."]}
    
    weekly = build_weekly_avaliability(availability)
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
                        "end": end_time
                        "minutes": alloc
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

    return {"ai_used": bool(ai_enabled), "sessions": sessions, "warnings": warnings}

    
    


