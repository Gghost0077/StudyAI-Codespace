# This file is the core of the scheduling logic 
# It takes the raw modules/tasks input into a clean list
# converts the weekkly availability into usable time slots 
# optionally adds AI tips and personalisation to the scheduling logic

# ======================
# Imports
# ======================
from datetime import datetime, timedelta, date # used for handling dates and times in the scheduling logic
from ai_service import get_study_tips_openai # imports the OpenAI helper from ai_service.py, which is used to generate study tips based on the tasks and their details.




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


# ====================
# Lightweight AI Personalisation and Tip Generation 
# ====================
# Applies simple AI-style priority nudges and returns explenations 

# defines a function that lightly adjusts tasks before scheduling based on their deadlines and the AI strictness level, 
# providing suggestions and explanations for any changes made to the task priorities.
def apply_ai_personalisation(tasks, ai_enabled, ai_strictness):
  
  # if AI is not enabled, it simply returns the original tasks along with empty lists for suggestions and explanations,
  #  ensuring that the scheduling logic can proceed without any AI modifications.
    if not ai_enabled:
        return tasks, [], []
# initialises two lists that will collect AI outputs 
    suggestions = []
    explanations = []
# sets the current date to compare against task deadlines, 
# allowing the function to determine how close each task is to its deadline 
# and adjust priorities accordingly.
    today = datetime.now().date()
# loops through every task and calculates how many days are left until the deadline
    for t in tasks:
        days_to_deadline = (t["deadline"] - today).days

# if the AI strictness is set to "high" and the deadline is within 3 days, 
# it increases the task's importance by 1 (up to a maximum of 3) 
# and adds a suggestion with an explanation for this change.
        if ai_strictness == "high" and days_to_deadline <= 3:
            old = t["importance"]
            t["importance"] = min(3, old + 1)
# builds a message explaining the reason for the priority increase, which is based on the proximity of the deadline,
            msg = f'Increased priority for "{t["title"]}" because deadline is in {days_to_deadline} days.'

# stores a structured suggestion object and a plain explanation message 
            suggestions.append({
                "task_title": t["title"],
                "priority_delta": t["importance"] - old,
                "explanation": msg
            })
            explanations.append(msg)

# if strictness is "medium" and the deadline is within 2 days, it does not change the priority but still adds a suggestion and explanation,
        elif ai_strictness == "medium" and days_to_deadline <= 2:
            msg = f'Consider starting "{t["title"]}" earlier (deadline in {days_to_deadline} days).'
            suggestions.append({
                "task_title": t["title"],
                "priority_delta": 0,
                "explanation": msg
            })
            explanations.append(msg)
# returns the updated tasks plus the AI messaging data 
    return tasks, suggestions, explanations

# ===========================================
# Fallback study tips generator that creates simple tips based on keywords in the task titles and descriptions
# ===========================================
def generate_study_tips_placeholder(tasks, ai_enabled):

   # if AI is disabled return no tips to avoid confusion  
    if not ai_enabled:
        return []
# creates the results list and loops through the tasks, looking for keywords in the title and description to generate simple study tips, 
# next steps, progression blocks, and session focus suggestions based on common task types like writing, exams, coding, and research.
    tips = []
    for t in tasks:
        text = f'{t.get("title","")} {t.get("description","")}'.lower()

        if any(k in text for k in ["essay", "report", "write", "draft", "structure"]):
            tip = "Break the writing into small sections and finish one section per session."
            next_step = "Write a short outline for the first section."
            progression_blocks = [
                "Understand the task brief",
                "Create an outline",
                "Draft each section",
                "Edit for clarity and structure",
                "Proofread and finalise",
            ]
            session_focus = "Draft the first section using your outline."
        elif any(k in text for k in ["exam", "revision", "test", "quiz"]):
            tip = "Use active recall and spaced repetition instead of rereading notes passively."
            next_step = "Create five quick practice questions from your notes."
            progression_blocks = [
                "Identify key topics",
                "Make questions or flashcards",
                "Test yourself regularly",
                "Review weak areas",
                "Do timed practice",
            ]
            session_focus = "Test yourself on one topic without looking at notes."
        elif any(k in text for k in ["coding", "program", "bug", "debug", "implement"]):
            tip = "Work feature by feature and test each part before moving on."
            next_step = "Implement one small part of the feature first."
            progression_blocks = [
                "Understand requirements",
                "Plan the solution",
                "Implement one part",
                "Test and debug",
                "Refine and document",
            ]
            session_focus = "Build and test one small feature component."
        elif any(k in text for k in ["research", "literature", "paper", "reading"]):
            tip = "Read strategically by skimming first and then taking short summary notes."
            next_step = "Skim one source and note three key points."
            progression_blocks = [
                "Skim the material",
                "Identify useful sections",
                "Take concise notes",
                "Compare sources",
                "Summarise findings",
            ]
            session_focus = "Read one source and capture its most useful ideas."
        else:
            tip = "Set a clear mini-goal so each session ends with visible progress."
            next_step = "Define one small outcome for this study session."
            progression_blocks = [
                "Understand the task",
                "Choose one small target",
                "Complete focused work",
                "Review what was done",
            ]
            session_focus = "Finish one small, clearly defined part of the task."

        tips.append({
            "task_title": t["title"],
            "module": t["module"],
            "tip": tip,
            "next_step": next_step,
            "progression_blocks": progression_blocks,
            "session_focus": session_focus,
        })

    return tips


# ===========================
# Time Helper Functions 
# ===========================

#Converts 'HH:MM' time strings into total minutes for easier calculations when building the schedule
def time_to_minutes(t: str) -> int:
    h, m = t.split(':')
    return int(h) * 60 + int(m)

# Converts minutes back into 'HH:MM' format for scheduling output,
# ensuring that the time slots in the generated schedule are presented 
# in a standard and easily understandable format for users.
def minutes_to_time(m: int) -> str:
    h = m // 60
    m = m % 60
    return f"{h:02d}:{m:02d}"

# turns a deadline string in the format 'YYYY-MM-DD' into a date object,
# allowing the scheduling logic to perform date comparisons and calculations based on task deadlines
def parse_deadline(d: str) -> date:
    return datetime.strptime(d, "%Y-%m-%d").date()

# ===========================
# Flattening and Sorting Tasks and Building Weekly Availability
# ===========================

# Convert nested module/task input into one flat sortable task list
def flatten_and_sort_tasks(modules):

    tasks = [] # initialises the output list 

    # for each module it pulls out module name, importance and optional brief text
    for m in modules: 
        module_name =  (m.get("name") or "").strip()
        importance = int(m.get("importance", 2)) # makes sure importance is numeric for sorting and defaults to 2 if missing or invalid
        module_brief_text = (m.get("brief_text") or "").strip()

    # loops through the tasks in each module, pulling out all the relevant fields and parsing the deadline,
    #  while also ensuring that only tasks with valid deadlines are included in the output list.
        for t in m.get("tasks", []):
            deadline_str  = t.get("deadline")
            if not deadline_str:
                continue
# builds the standard task object used by the rest of the scheduling logic, ensuring that all necessary fields are present and
#  properly formatted for later use in the schedule generation.
            tasks.append({
                    "module": module_name,
                    "importance": importance,
                    "title": (t.get("title") or "").strip(),
                    "description": (t.get("description") or "").strip(),
                    "module_brief_text": module_brief_text,
                    "task_type": (t.get("task_type") or "").strip(),
                    "current_progress": (t.get("current_progress") or "").strip(),
                    "biggest_difficulty": (t.get("biggest_difficulty") or "").strip(),
                    "goal": (t.get("goal") or "").strip(),
                    "deadline": parse_deadline(deadline_str),
                    "minutes_needed": int(float(t.get("estimated_hours", 0)) * 60),
                })
    # Sort tasks by deadline, then by importance (descending)
    tasks.sort(key=lambda x: (x["deadline"], -x["importance"]))
    return tasks

# creates a dictiornary where each key is a weekday number (0-6) and the value is a list of available time intervals for that day,
#  based on the user's input availability. This structured format allows the scheduling logic 
# to easily access and allocate time slots for tasks on specific days of the week when generating the schedule.
def build_weekly_availability(availability):
    weekly = {i: [] for i in range(7)}

# gets the day name and converts it to a weekday number for each availability slot
    for slot in availability:
        day = slot.get("day")
        wd = DAY_TO_WEEKDAY.get(day)
#skips invalid day names that are not in the mapping, ensuring that only valid availability entries are processed and included in the weekly structure.
        if wd is None:
            continue

#pulls the the start and end times for each availability slot, and converts them into minutes for easier calculations later on when building the schedule.
        start = slot.get("start")
        end = slot.get("end")
#skips any availability entries that are missing start or end times, ensuring that only complete and valid time intervals are included in the weekly availability structure.
        if not start or not end:
            continue
#converts start and end strings into numeric minutes
        s = time_to_minutes(start)
        e = time_to_minutes(end)
# only adds valid intervals where the start time is before the end time, preventing any nonsensical time slots from being included in the weekly availability.
        if s < e:
            weekly[wd].append((s, e))

    # Sort intervals for each day in cronological order and returns the final structured weekly availability dict, 
    # which will be used to build the free calendar for scheduling tasks.
    for wd in weekly:
        weekly[wd].sort()

    return weekly

# expands the weekly availability into a daily calendar of free time slots from today until the last task deadline,
def build_free_calendar(today, last_day, weekly):

# starts from today and goes day by day until the last deadline. For each day,
# it looks up the corresponding weekday in the weekly availability and copies 
# those time intervals into the free calendar for that specific date.
    free = {}
    d = today 
    while d <= last_day:
        free[d] = weekly.get(d.weekday(), []).copy()  # Start with weekly availability for that day
        d += timedelta(days=1)
    return free

# ===========================
# Main Schedule Generation Logic
# ===========================


# This function takes the list of modules and their tasks, the user's weekly availability, and AI settings to generate a study schedule.
def generate_schedule(modules, availability, ai_enabled=False, ai_strictness="medium", chunk_minutes=60):

    # uses the flatten_and_sort_tasks function to convert the nested module/task input into a single flat list of tasks, sorted by deadline and importance.
    tasks = flatten_and_sort_tasks(modules)
    # if there are no valid tasks with deadlines, it returns an empty schedule along with a warning message, while still indicating whether AI was enabled or not.
    if not tasks:
        return {"ai_used": bool(ai_enabled), 
                "sessions": [], 
                "warnings": ["No valid tasks with deadlines found."],
                "ai_suggestions": [],
                "ai_explanations": []
                }
    # applies the AI personalisation function to the list of tasks, which may adjust task priorities based on their 
    # deadlines and the specified AI strictness level, 
    # while also collecting any suggestions and explanations generated by the AI for these adjustments.
    tasks, ai_suggestions, ai_explanations = apply_ai_personalisation(
        tasks, bool(ai_enabled), ai_strictness
    )

# builds a simplified list of deadline markers that can be used in the frontend calendar UI to visually indicate when task deadlines are approaching,
    deadline_markers = []

    for task in tasks:
        deadline_markers.append({
            "module": task["module"],
            "title": task["title"],
            "date": task["deadline"].isoformat(),
            "type": "deadline"
        })

# if ai is enabled, it attempts to generate study tips using the OpenAI helper function, passing in the tasks and the AI strictness level.
    ai_tips = []
    if bool(ai_enabled):
        try:
            ai_tips = get_study_tips_openai(tasks, strictness=ai_strictness)
# if ai fails for any reason (e.g. API error, network issue), it catches the exception
# and falls back to the placeholder tip generator to ensure that the scheduling process can still provide some form of study tips to the user without crashing.
        except Exception as e:
            print("AI tip generation failed:", e, flush=True)
            ai_tips = generate_study_tips_placeholder(tasks, True)
# if AI is not enabled, it simply sets ai_tips to an empty list, ensuring that the rest of the scheduling logic can proceed without any AI-generated tips.
    else:
        ai_tips = []

    # Re sorts after AI adjustments (if importance changed)
    tasks.sort(key=lambda x: (x["deadline"], -x["importance"]))
    # converts user availability into a weekday-number time slots 
    weekly = build_weekly_availability(availability)

# sets today as the starting point for scheduling and determines the last day to consider based on the latest task deadline
    today = datetime.now().date()
    last_day = max(t["deadline"] for t in tasks)
    free = build_free_calendar(today, last_day, weekly) 
    sessions = []
    warnings = []

# for each task, it checks how many minutes are needed and tries to allocate time slots for that task in the free calendar before the task's deadline. 
# does this by iterating through the days from today until the deadline, looking for available time intervals, 
# and filling those intervals with study sessions of a specified chunk size (e.g., 60 minutes) until the task is fully scheduled or there are no more available slots before the deadline.
    for task in tasks:
        remaining = task["minutes_needed"]
        if remaining <= 0:
            continue

# walks day by day from today up to the task's deadline, checking the free calendar for available time intervals on each day. If it finds intervals,
#  it allocates study sessions in chunks until either the task is fully scheduled or there are no more intervals left before the deadline.
        d = today 
        while d <= task["deadline"] and remaining > 0:
            intervals = free.get(d, [])
            if not intervals:
                d += timedelta(days=1)
                continue

# for each available interval on that day, it tries to fit as many study sessions as possible, each of a specified chunk size, 
# until the task's remaining minutes are fully allocated or the end of the interval is reached.
            new_intervals = []
            for (s, e) in intervals:
                cursor = s
                # allocates study sessions in chunks until either the task is fully scheduled or there are no more intervals left before the deadline.
                while cursor < e and remaining > 0:
                    alloc = min(chunk_minutes, e - cursor, remaining)
                    # turns the allocated time in minutes back into 'HH:MM' format for the schedule output, 
                    # ensuring that the scheduled sessions are presented in a user-friendly time format.
                    start_time = minutes_to_time(cursor)
                    end_time = minutes_to_time(cursor + alloc)
                    
                    # creates one session entry for the schedule with all the relevant details, including the module, task title, date, start and end times, 
                    # allocated minutes, source of scheduling (rule-based), and a note indicating that it was scheduled before the deadline.
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

# moves forward the cursor by the allocated time and reduces the remaining minutes needed for the task. 
# If there is still time left in the interval after allocation,
                    cursor += alloc
                    remaining -= alloc
                # if some of the interval is still free after scheduling sessions,
                #  it adds the remaining free time back into the new intervals list for that day,
                if cursor < e:
                    new_intervals.append((cursor, e))
            # updates the days remaining free time and moves on to the next day. 
            free[d] = new_intervals
            d += timedelta(days=1)
        
        # if the task could not be fully scheduled before its deadline, record a warning
        if remaining > 0:
            warnings.append(f"not enough time to fully schedule '{task['title']}' (missing {remaining}) minutes")

# returns the full response object containing whether AI was used, the list of scheduled sessions, deadline markers for the calendar, any warnings about unscheduled time,
#  AI-generated suggestions and explanations, the AI strictness level, and any study tips generated by the AI or the placeholder function.
#  This structured response will be used by the frontend to display the schedule and related information to the user.
    return {"ai_used": bool(ai_enabled), 
            "sessions": sessions, 
            "deadlines": deadline_markers,
            "warnings": warnings,
            "ai_suggestions": ai_suggestions,
            "ai_explanations": ai_explanations,
            "ai_strictness": ai_strictness,
            "ai_tips": ai_tips
            }

    
    


