//Frontend JavaScript for Schedule Generator App

// DOM elements connecting Javascript to the static HTML elements.
const modulesContainer = document.getElementById("modulesContainer");
const addModuleBtn = document.getElementById("addModuleBtn");
const availabilityContainer = document.getElementById("availabilityContainer");
const addAvailabilityBtn = document.getElementById("addAvailabilityBtn");

// UI Creation Functions
// These functions create the necessary HTML blocks for modules, tasks, and availability slots dynamically
// when the user clicks the "Add" buttons. They also set up the structure for user input
// and the remove buttons for each block.
function createModuleBlock() {
  const moduleDiv = document.createElement("div");
  moduleDiv.classList.add("card", "shadow-sm", "mb-4");

  moduleDiv.innerHTML = `
  <div class="card-body">
    <div class="d-flex justify-content-between align-items-start mb-2">
      <div class="w-100 me-2">
        <label class="form-label">Module Name</label>
        <input type="text" class="form-control module-name" placeholder="e.g., COM6016M" />
      </div>
      <button type="button" class="btn btn-sm btn-outline-danger removeModuleBtn mt-4">
        <i class="bi bi-x-lg"></i>
      </button>
    </div>

    <div class="mb-2">
      <label class="form-label">Importance (1–3)</label>
      <select class="form-select module-importance">
        <option value="1">1 (Low)</option>
        <option value="2" selected>2 (Medium)</option>
        <option value="3">3 (High)</option>
      </select>
    </div>

    <hr />

    <div class="d-flex justify-content-between align-items-center mb-2">
      <strong>Tasks</strong>
      <button type="button" class="btn btn-sm btn-outline-primary addTaskBtn">
        <i class="bi bi-plus-lg"></i> Add Task
      </button>
    </div>

    <div class="tasksContainer"></div>
  </div>

  `;

  modulesContainer.appendChild(moduleDiv);

  // Get the tasksContainer for adding the default task
  const tasksContainer = moduleDiv.querySelector(".tasksContainer");

  // Add one task by default
  createTaskBlock(tasksContainer);
}

function createTaskBlock(container) {
  const taskDiv = document.createElement("div");
  taskDiv.classList.add("task-block");
  taskDiv.classList.add("border", "rounded", "p-3", "mb-3", "bg-body-tertiary");

  taskDiv.innerHTML = `
    <div class="mb-2">
      <label class="form-label">Task Title</label>
      <input type="text" class="form-control task-title"
        placeholder="e.g., Essay Draft" />
    </div>

    <div class="mb-2">
      <label class="form-label">Task Description</label>
      <textarea class="form-control task-desc" rows="2"
        placeholder="Brief description of what needs to be done"></textarea>
    </div>

    <div class="row g-2 mb-2">
      <div class="col-6">
        <label class="form-label">Deadline</label>
        <input type="date" class="form-control task-deadline" />
      </div>
      <div class="col-6">
        <label class="form-label">Estimated Hours</label>
        <input type="number" class="form-control task-hours" min="1" step="0.5" />
      </div>
    </div>

    <button class="btn btn-sm btn-outline-danger removeTaskBtn">
      Remove Task
    </button>
  `;

  container.appendChild(taskDiv);
}

function createAvailabilityBlock() {
  const slot = document.createElement("div");
  slot.classList.add("border", "rounded", "p-3", "mb-3", "bg-body");
  slot.classList.add("availability-block");

  slot.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-2">
      <strong class="small">Availability Slot</strong>
      <button type="button" class="btn btn-sm btn-outline-danger removeAvailabilityBtn">
        Remove
      </button>
    </div>

    <div class="mb-2">
      <label class="form-label">Day</label>
      <select class="form-select availability-day">
        <option value="Monday">Monday</option>
        <option value="Tuesday">Tuesday</option>
        <option value="Wednesday">Wednesday</option>
        <option value="Thursday">Thursday</option>
        <option value="Friday">Friday</option>
        <option value="Saturday">Saturday</option>
        <option value="Sunday">Sunday</option>
      </select>
    </div>

    <div class="row g-2">
      <div class="col-6">
        <label class="form-label">Start</label>
        <input type="time" class="form-control availability-start" />
      </div>
      <div class="col-6">
        <label class="form-label">End</label>
        <input type="time" class="form-control availability-end" />
      </div>
    </div>
  `;

  availabilityContainer.appendChild(slot);
}

///////////////////////////////////////////////////////
// Functions to get modules from the index page for schedule generation
///////////////////////////////////////////////////////

function getModules() {
  const modules = [];

  document
    .querySelectorAll("#modulesContainer > div")
    .forEach((moduleBlock) => {
      const module = {
        name: moduleBlock.querySelector(".module-name").value.trim(),
        importance: Number(
          moduleBlock.querySelector(".module-importance").value,
        ),
        tasks: [],
      };

      moduleBlock
        .querySelectorAll(".tasksContainer > div")
        .forEach((taskBlock) => {
          module.tasks.push({
            title: taskBlock.querySelector(".task-title").value.trim(),
            description: taskBlock.querySelector(".task-desc").value.trim(),
            deadline: taskBlock.querySelector(".task-deadline").value,
            estimated_hours: Number(
              taskBlock.querySelector(".task-hours").value,
            ),
          });
        });

      modules.push(module);
    });

  return modules;
}

///////////////////////////////////////////////////////
///// functions to get availability slots from the index page for schedule generation
///////////////////////////////////////////////////////

function getAvailabilitySlots() {
  const slots = [];

  document
    .querySelectorAll("#availabilityContainer .availability-block")
    .forEach((block) => {
      slots.push({
        day: block.querySelector(".availability-day").value,
        start: block.querySelector(".availability-start").value,
        end: block.querySelector(".availability-end").value,
      });
    });

  return slots;
}

////////////////////////////////////////////
//  Form Validation (basic example, can be expanded)
////////////////////////////////////////////

function validateForm() {
  const modules = getModules();
  const availability = getAvailabilitySlots();

  if (modules.length === 0) {
    return "Please add at least one module.";
  }

  for (const module of modules) {
    if (!module.name) {
      return "Please enter a name for all modules.";
    }
    if (module.tasks.length === 0) {
      return `Please add at least one task for module ${module.name}.`;
    }
    for (const task of module.tasks) {
      if (!task.title) {
        return `Please enter a title for all tasks in module ${module.name}.`;
      }
      if (!task.deadline) {
        return `Please set a deadline for all tasks in module ${module.name}.`;
      }
      if (!task.estimated_hours || task.estimated_hours <= 0) {
        return `Please enter a valid estimated hours for task "${task.title}" in module ${module.name}.`;
      }
    }
  }
  // Validate availability slots
  if (availability.length === 0) {
    return "Please add at least one availability slot.";
  }

  for (const slot of availability) {
    if (!slot.start || !slot.end) {
      return "Please set both start and end times for all availability slots.";
    }
    if (slot.start >= slot.end) {
      return "Start time must be before end time in availability slots.";
    }
  }

  return null; // No errors
}

// Initial setup

createModuleBlock(); // Create the first module input block on page load
createAvailabilityBlock(); // Create the first availability block ONCE

// Handle all availability-related clicks (remove availability)
availabilityContainer.addEventListener("click", (e) => {
  if (e.target.closest(".removeAvailabilityBtn")) {
    e.target.closest(".availability-block").remove();
  }
});

// Handle all module-related clicks (add task, remove module, remove task)
modulesContainer.addEventListener("click", (e) => {
  if (e.target.closest(".addTaskBtn")) {
    const moduleCard = e.target.closest(".card");
    const tasksContainer = moduleCard.querySelector(".tasksContainer");
    createTaskBlock(tasksContainer);
  } else if (e.target.closest(".removeModuleBtn")) {
    e.target.closest(".card").remove();
  } else if (e.target.closest(".removeTaskBtn")) {
    e.target.closest(".task-block").remove();
  }
});

// Handle static button clicks
addModuleBtn.addEventListener("click", createModuleBlock);
addAvailabilityBtn.addEventListener("click", createAvailabilityBlock);

//////////////////////////////////////////
// Calendar Renderer Function
//////////////////////////////////////////

function timeToMinutes(t) {
  const [h, m] = t.split(":").map(Number);
  return h * 60 + m;
}

//Converts "YYYY-MM-DD" to Date object
function parseISODate(dateStr) {
  const [y, m, d] = dateStr.split("-").map(Number);
  return new Date(y, m - 1, d);
}

// Finds the Monday of the week for a given date for the Anchor of the week in the calendar view
function getMonday(d) {
  const date = new Date(d);
  const day = date.getDay();
  const diff = (day === 0 ? -6 : 1) - day; // shift to Monday
  date.setDate(date.getDate() + diff);
  date.setHours(0, 0, 0, 0);
  return date;
}

// Build list of the 7 Dates
function buildWeekDays(weekStart) {
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(weekStart);
    d.setDate(d.getDate() + i);
    return d;
  });
}

// Main function to render the weekly calendar view based on the generated schedule sessions
function renderWeeklyCalendar(container, sessions) {
  container.innerHTML = ""; // Clear previous content

  const valid = sessions.filter((s) => s.date && s.start && s.end); // Only consider sessions with valid date and time

  if (valid.length === 0) {
    container.innerHTML = `<div class="text-muted">No sessions with valid date/time to display.</div>`;
    return;
  }

  const earliest = valid
    .map((s) => parseISODate(s.date))
    .sort((a, b) => a - b)[0];

  const weekStart = getMonday(earliest);
  const days = buildWeekDays(weekStart);

  // Header row with days of the week
  const cal = document.createElement("div");
  cal.className = "weekly-calendar";

  const empty = document.createElement("div");
  empty.className = "calendar-header time-col-header";
  cal.appendChild(empty);

  days.forEach((d) => {
    const head = document.createElement("div");
    head.className = "calendar-header";
    head.textContent = d.toLocaleDateString(undefined, {
      weekday: "short",
      day: "2-digit",
      month: "short",
    });
    cal.appendChild(head);
  });

  // Time slots (e.g., 8:00 to 20:00)

  const startHour = 6;
  const endHour = 22;

  const timeCol = document.createElement("div");
  timeCol.className = "time-col";

  for (let hour = startHour; hour <= endHour; hour++) {
    const label = document.createElement("div");
    label.className = "time-label";
    label.textContent = `${String(hour).padStart(2, "0")}:00`;
    timeCol.appendChild(label);
  }

  cal.appendChild(timeCol);

  // Add 7 empty day columns with grids for sessions to be placed in
  const hourHeight = 60; // pixels per hour

  days.forEach((dayDate) => {
    const dayCol = document.createElement("div");
    dayCol.className = "day-col";

    const grid = document.createElement("div");
    grid.className = "day-grid";
    grid.style.height = `${(endHour - startHour) * hourHeight}px`;

    for (let hour = startHour; hour < endHour; hour++) {
      const line = document.createElement("div");
      line.className = "hour-line";
      grid.appendChild(line);
    }

    // Place sessions in the correct position

    const dayKey = dayDate.toISOString().slice(0, 10); // "YYYY-MM-DD"
    const daySessions = valid.filter((s) => s.date === dayKey);

    daySessions.forEach((s) => {
      const startMins = timeToMinutes(s.start);
      const endMins = timeToMinutes(s.end);

      const startClamp = Math.max(startMins, startHour * 60);
      const endClamp = Math.min(endMins, endHour * 60);
      if (endClamp <= startClamp) return; // Skip sessions outside of display range

      const top = ((startClamp - startHour * 60) / 60) * hourHeight;
      const height = ((endClamp - startClamp) / 60) * hourHeight;

      const block = document.createElement("div");
      block.className = "session-block";
      block.style.top = `${top}px`;
      block.style.height = `${height}px`;

      block.innerHTML = `
        <div class="title">${s.title ?? "Untitled"}</div>
        <div class="meta">${s.module ?? ""} • ${s.start}–${s.end}</div>
  `;
      grid.appendChild(block);
    });

    dayCol.appendChild(grid);
    cal.appendChild(dayCol);
  });

  container.appendChild(cal);
}

/////////////////////////////////////////////

const generateBtn = document.getElementById("generateBtn");
generateBtn.addEventListener("click", async () => {
  const error = validateForm();
  if (error) {
    alert(error); // Simple for now
    return;
  }
  //////////////////////////
  //Data Package to get sent to backend
  //////////////////////////
  const payload = {
    modules: getModules(),
    availability: getAvailabilitySlots(),
    ai_enabled: document.getElementById("aiEnabled").checked,
    ai_strictness: document.getElementById("aiStrictness").value, // low|medium|high
  };

  try {
    const res = await fetch("http://127.0.0.1:5000/generate_schedule", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      console.error("Backend error:", data);
      alert(data.error || "Backend error");
      return;
    }

    console.log("Schedule returned:", data);
    // Render schedule nicely in the UI
    const scheduleView = document.getElementById("scheduleView");

    if (scheduleView) {
      scheduleView.innerHTML = ""; // clear previous results

      // AI status badge
      const aiUsed = Boolean(data.ai_used);
      const badgeWrapper = document.createElement("div");
      badgeWrapper.classList.add("mb-3");

      badgeWrapper.innerHTML = `
    <span class="badge ${aiUsed ? "bg-success" : "bg-secondary"}">
      ${aiUsed ? "AI enabled" : "Rule-based only"}
    </span>
  `;

      scheduleView.appendChild(badgeWrapper);

      // Render AI explanations (if any)
      if (
        Array.isArray(data.ai_explanations) &&
        data.ai_explanations.length > 0
      ) {
        const expl = document.createElement("div");
        expl.className = "alert alert-info";
        expl.innerHTML = `
          <strong>AI explanations</strong>
          <ul class="mb-0">
            ${data.ai_explanations.map((e) => `<li>${e}</li>`).join("")}
          </ul>
        `;
        scheduleView.appendChild(expl);
      }

      // Render AI suggestions (if any)
      if (
        Array.isArray(data.ai_suggestions) &&
        data.ai_suggestions.length > 0
      ) {
        const sug = document.createElement("div");
        sug.className = "card mb-3 shadow-sm";
        sug.innerHTML = `
          <div class="card-body">
            <strong>AI suggestions</strong>
            <ul class="mb-0">
              ${data.ai_suggestions
                .map(
                  (s) =>
                    `<li><strong>${s.task_title ?? "Task"}</strong>: ${
                      s.explanation ?? JSON.stringify(s)
                    }</li>`,
                )
                .join("")}
            </ul>
          </div>
        `;
        scheduleView.appendChild(sug);
      }

      // Render sessions
      const sessions = Array.isArray(data.sessions) ? data.sessions : [];

      if (sessions.length === 0) {
        scheduleView.innerHTML += `<div class="text-muted">No sessions generated.</div>`;
      } else {
        renderWeeklyCalendar(scheduleView, sessions, {
          startHour: 6,
          endHour: 22,
        });
      }
    }
  } catch (err) {
    console.error("Fetch Failed", err);
    alert("Could not reach backend. Is Flask running?" + err.message);
  }
});
