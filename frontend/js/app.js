//Frontend JavaScript for Schedule Generator App

// DOM elements connecting Javascript to the static HTML elements
// .
const API_BASE_URL = window.location.origin;
const modulesContainer = document.getElementById("modulesContainer");
const addModuleBtn = document.getElementById("addModuleBtn");
const availabilityContainer = document.getElementById("availabilityContainer");
const addAvailabilityBtn = document.getElementById("addAvailabilityBtn");
const regenerateBtn = document.getElementById("regenerateBtn");

const consentScreen = document.getElementById("consentScreen");
const appShell = document.getElementById("appShell");
const consentCheckbox = document.getElementById("consentCheckbox");
const consentContinueBtn = document.getElementById("consentContinueBtn");

//Consent  form Functions
function hasConsented() {
  return localStorage.getItem("studyAI_consentGiven") === "true";
}

function setConsentGiven() {
  localStorage.setItem("studyAI_consentGiven", "true");
}

function showAppAfterConsent() {
  if (consentScreen) consentScreen.style.display = "none";
  if (appShell) appShell.style.display = "block";
}

function showConsentScreen() {
  if (consentScreen) consentScreen.style.display = "block";
  if (appShell) appShell.style.display = "none";
}

// Participant ID function

function getParticipantId() {
  let participantId = localStorage.getItem("studyAI_participantId");

  if (!participantId) {
    participantId = `participant-${crypto.randomUUID()}`;
    localStorage.setItem("studyAI_participantId", participantId);
  }

  return participantId;
}

// Research event logging
async function logEvent(eventType, extraData = {}) {
  const payload = {
    participant_id: getParticipantId(),
    event_type: eventType,
    timestamp: new Date().toISOString(),
    ...extraData,
  };

  try {
    await fetch(`${API_BASE_URL}/log_event`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (err) {
    console.error("Log event failed:", err);
  }
}

// Deadline Function to build deadline data to show in calendar

function buildUpcomingDeadlines(modules) {
  const deadlines = [];

  modules.forEach((module) => {
    (module.tasks || []).forEach((task) => {
      if (!task.deadline) return;

      const today = new Date();
      today.setHours(0, 0, 0, 0);

      const deadlineDate = new Date(task.deadline);
      deadlineDate.setHours(0, 0, 0, 0);

      const diffMs = deadlineDate - today;
      const daysRemaining = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

      deadlines.push({
        module: module.name,
        title: task.title,
        deadline: task.deadline,
        daysRemaining,
      });
    });
  });

  deadlines.sort((a, b) => new Date(a.deadline) - new Date(b.deadline));
  return deadlines;
}

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

///////////////////////////////
// Availability preset helpers
///////////////////////////////

function addAvailabilitySlot(day, start, end) {
  // create a new blank slot in the UI
  createAvailabilityBlock();

  // get the slot we just added (last one)
  const blocks = availabilityContainer.querySelectorAll(".availability-block");
  const newBlock = blocks[blocks.length - 1];

  // fill in values
  newBlock.querySelector(".availability-day").value = day;
  newBlock.querySelector(".availability-start").value = start; // "HH:MM"
  newBlock.querySelector(".availability-end").value = end; // "HH:MM"
}

function clearAvailabilitySlots() {
  availabilityContainer.innerHTML = "";
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

// Save current website state so schedule doesnt disapear when reset
function saveAppState() {
  const appState = {
    modules: getModules(),
    availability: getAvailabilitySlots(),
    ai_enabled: document.getElementById("aiEnabled")?.checked ?? false,
    ai_strictness: document.getElementById("aiStrictness")?.value ?? "medium",
  };

  localStorage.setItem("studyAIState", JSON.stringify(appState));
}

// Loads the app state
function loadAppState() {
  const saved = localStorage.getItem("studyAIState");

  if (!saved) {
    createModuleBlock();
    createAvailabilityBlock();
    return;
  }

  const state = JSON.parse(saved);

  // Clear existing UI first
  modulesContainer.innerHTML = "";
  availabilityContainer.innerHTML = "";

  // Restore modules and tasks
  if (Array.isArray(state.modules) && state.modules.length > 0) {
    state.modules.forEach((module) => {
      createModuleBlock();

      const moduleBlocks = modulesContainer.querySelectorAll(".card");
      const moduleBlock = moduleBlocks[moduleBlocks.length - 1];

      moduleBlock.querySelector(".module-name").value = module.name ?? "";
      moduleBlock.querySelector(".module-importance").value = String(
        module.importance ?? 2,
      );

      const tasksContainer = moduleBlock.querySelector(".tasksContainer");
      tasksContainer.innerHTML = "";

      if (Array.isArray(module.tasks) && module.tasks.length > 0) {
        module.tasks.forEach((task) => {
          createTaskBlock(tasksContainer);

          const taskBlocks = tasksContainer.querySelectorAll(".task-block");
          const taskBlock = taskBlocks[taskBlocks.length - 1];

          taskBlock.querySelector(".task-title").value = task.title ?? "";
          taskBlock.querySelector(".task-desc").value = task.description ?? "";
          taskBlock.querySelector(".task-deadline").value = task.deadline ?? "";
          taskBlock.querySelector(".task-hours").value =
            task.estimated_hours ?? "";
        });
      }
    });
  } else {
    createModuleBlock();
  }

  // Restore availability
  if (Array.isArray(state.availability) && state.availability.length > 0) {
    state.availability.forEach((slot) => {
      createAvailabilityBlock();

      const blocks = availabilityContainer.querySelectorAll(
        ".availability-block",
      );
      const block = blocks[blocks.length - 1];

      block.querySelector(".availability-day").value = slot.day ?? "Monday";
      block.querySelector(".availability-start").value = slot.start ?? "";
      block.querySelector(".availability-end").value = slot.end ?? "";
    });
  } else {
    createAvailabilityBlock();
  }

  // Restore AI settings
  const aiEnabled = document.getElementById("aiEnabled");
  if (aiEnabled) aiEnabled.checked = state.ai_enabled ?? false;

  const aiStrictness = document.getElementById("aiStrictness");
  if (aiStrictness) aiStrictness.value = state.ai_strictness ?? "medium";
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

if (hasConsented()) {
  showAppAfterConsent();
  loadAppState();
  logEvent("app_opened");
} else {
  showConsentScreen();
}

// Display participant ID on the page
const participantInfo = document.getElementById("participantInfo");
if (participantInfo) {
  participantInfo.innerHTML = `
    <span class="badge bg-secondary">
      Participant ID: ${getParticipantId()}
    </span>
  `;
}

//Consent button listener

if (consentCheckbox && consentContinueBtn) {
  consentCheckbox.addEventListener("change", () => {
    consentContinueBtn.disabled = !consentCheckbox.checked;
  });

  consentContinueBtn.addEventListener("click", () => {
    setConsentGiven();
    showAppAfterConsent();
    loadAppState();
    logEvent("consent_given");
    logEvent("app_opened");
  });
}

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

if (regenerateBtn) {
  regenerateBtn.addEventListener("click", () => {
    generateBtn.click();
  });
}

// Event Listeners for save app state and load app state
modulesContainer.addEventListener("input", saveAppState);
availabilityContainer.addEventListener("input", saveAppState);

const aiEnabled = document.getElementById("aiEnabled");
if (aiEnabled) {
  aiEnabled.addEventListener("change", saveAppState);
}

const aiStrictness = document.getElementById("aiStrictness");
if (aiStrictness) {
  aiStrictness.addEventListener("change", saveAppState);
}

////////////////////
// Availability Preset Buttons
////////////////////

document
  .getElementById("presetWeekdayEvenings")
  .addEventListener("click", () => {
    // Mon–Fri 18:00–20:00
    clearAvailabilitySlots();
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"].forEach((day) => {
      addAvailabilitySlot(day, "18:00", "20:00");
    });
  });

document
  .getElementById("presetWeekdayMornings")
  .addEventListener("click", () => {
    // Mon–Fri 09:00–11:00
    clearAvailabilitySlots();
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"].forEach((day) => {
      addAvailabilitySlot(day, "09:00", "11:00");
    });
  });

document.getElementById("presetWeekends").addEventListener("click", () => {
  // Sat–Sun 10:00–13:00
  clearAvailabilitySlots();
  ["Saturday", "Sunday"].forEach((day) => {
    addAvailabilitySlot(day, "10:00", "13:00");
  });
});

document
  .getElementById("presetClearAvailability")
  .addEventListener("click", () => {
    clearAvailabilitySlots();
    // optional: add one blank slot back so the UI isn't empty
    createAvailabilityBlock();
  });

//////////////////////////////////////////
// Calendar Renderer Function Helper
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

function getModuleColor(moduleName) {
  const colors = [
    { bg: "#e9f2ff", border: "#4a7cff" },
    { bg: "#eefaf0", border: "#2e9d57" },
    { bg: "#fff4e6", border: "#f08c00" },
    { bg: "#f3e8ff", border: "#8b5cf6" },
    { bg: "#ffe8e8", border: "#e03131" },
    { bg: "#e6fcf5", border: "#0ca678" },
  ];

  let hash = 0;
  const text = moduleName || "default";

  for (let i = 0; i < text.length; i++) {
    hash += text.charCodeAt(i);
  }

  return colors[hash % colors.length];
}
////////////////////////////////////////////////
// Main function to render the weekly calendar view based on the generated schedule sessions
////////////////////////////////////////////////

// allows for changing of weeks in calendar
let currentCalendarWeekStart = null; // stores the monday of the week currently showing
let latestCalendarSessions = []; // stores the last generated calendar allowing us to go back and forth

function renderWeeklyCalendar(container, sessions) {
  container.innerHTML = ""; // Clear previous content

  const valid = sessions.filter((s) => s.date && s.start && s.end); // Only consider sessions with valid date and time

  if (valid.length === 0) {
    container.innerHTML = `
      <div class="card shadow-sm">
        <div class="card-body text-center py-4">
          <div class="fs-5 mb-2">No schedule generated yet</div>
          <div class="text-muted small">
            Add modules, tasks, and availability, then click
            <strong>Generate Schedule</strong> to view your weekly plan.
          </div>
        </div>
      </div>
    `;
    return;
  }

  const earliest = valid
    .map((s) => parseISODate(s.date))
    .sort((a, b) => a - b)[0];

  if (!currentCalendarWeekStart) {
    currentCalendarWeekStart = getMonday(earliest);
  }

  const weekStart = new Date(currentCalendarWeekStart);
  const days = buildWeekDays(weekStart);

  // Calendar Header
  const weekEnd = new Date(weekStart);
  weekEnd.setDate(weekEnd.getDate() + 6);

  const header = document.createElement("div");
  header.className = "d-flex justify-content-between align-items-center mb-3";

  header.innerHTML = `
    <div>
      <h5 class="mb-0">Weekly Schedule</h5>
      <small class="text-muted">
        Week of ${weekStart.toLocaleDateString(undefined, {
          day: "2-digit",
          month: "short",
        })} – ${weekEnd.toLocaleDateString(undefined, {
          day: "2-digit",
          month: "short",
          year: "numeric",
        })}
      </small>
    </div>

    <div class="btn-group btn-group-sm" role="group">
      <button type="button" class="btn btn-outline-secondary" id="prevWeekBtn">
        ← Previous
      </button>
      <button type="button" class="btn btn-outline-secondary" id="nextWeekBtn">
        Next →
      </button>
    </div>
  `;

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
      block.className = "calendar-session shadow-sm";
      block.style.top = `${top}px`;
      block.style.height = `${height}px`;
      //
      const moduleColor = getModuleColor(s.module);
      block.style.backgroundColor = moduleColor.bg;
      block.style.borderLeft = `4px solid ${moduleColor.border}`;

      block.innerHTML = `
        <div class="title">${s.title ?? "Untitled"}</div>
        <div class="meta">${s.module ?? ""} • ${s.start}–${s.end}</div>
  `;
      grid.appendChild(block);
    });

    dayCol.appendChild(grid);
    cal.appendChild(dayCol);
  });

  container.appendChild(header);
  container.appendChild(cal);

  const prevWeekBtn = container.querySelector("#prevWeekBtn");
  const nextWeekBtn = container.querySelector("#nextWeekBtn");

  if (prevWeekBtn) {
    prevWeekBtn.addEventListener("click", () => {
      const newWeek = new Date(currentCalendarWeekStart);
      newWeek.setDate(newWeek.getDate() - 7);
      currentCalendarWeekStart = newWeek;
      renderWeeklyCalendar(container, latestCalendarSessions);
    });
  }

  if (nextWeekBtn) {
    nextWeekBtn.addEventListener("click", () => {
      const newWeek = new Date(currentCalendarWeekStart);
      newWeek.setDate(newWeek.getDate() + 7);
      currentCalendarWeekStart = newWeek;
      renderWeeklyCalendar(container, latestCalendarSessions);
    });
  }
}

/////////////////////////////////////////////

const generateBtn = document.getElementById("generateBtn");
generateBtn.addEventListener("click", async () => {
  const error = validateForm();
  if (error) {
    alert(error); // Simple for now
    return;
  }
  // Show loading state
  generateBtn.disabled = true;
  generateBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Generating...`;
  //////////////////////////
  //Data Package to get sent to backend
  //////////////////////////
  const payload = {
    modules: getModules(),
    availability: getAvailabilitySlots(),
    ai_enabled: document.getElementById("aiEnabled").checked,
    ai_strictness: document.getElementById("aiStrictness").value, // low|medium|high
  };

  const upcomingDeadlines = buildUpcomingDeadlines(payload.modules);

  try {
    const res = await fetch(`${API_BASE_URL}/generate_schedule`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      console.error("Backend error:", data);

      // Restore button if backend returns an error
      generateBtn.disabled = false;
      generateBtn.innerHTML = `<i class="bi bi-magic me-1"></i>Generate Schedule`;

      alert(data.error || "Backend error");
      return;
    }

    console.log("Schedule returned:", data);
    // Render schedule nicely in the UI
    const scheduleView = document.getElementById("scheduleView");

    if (scheduleView) {
      scheduleView.innerHTML = ""; // clear previous results

      // AI status badg
      const aiUsed = Boolean(data.ai_used);
      const badgeWrapper = document.createElement("div");
      badgeWrapper.classList.add("mb-3");

      badgeWrapper.innerHTML = `
    <span class="badge ${aiUsed ? "bg-success" : "bg-secondary"}">
      ${aiUsed ? "AI enabled" : "Rule-based only"}
    </span>
  `;

      scheduleView.appendChild(badgeWrapper);

      //////////////////////////////////////
      // Schedule summary bar (showing small card with what the schedule generated has)
      /////////////////////////////////////
      const sessions = Array.isArray(data.sessions) ? data.sessions : [];
      latestCalendarSessions = sessions;
      currentCalendarWeekStart = null;

      const warnings = Array.isArray(data.warnings) ? data.warnings : [];

      const totalMinutes = sessions.reduce(
        (sum, s) => sum + (s.minutes ?? 0),
        0,
      );
      const totalHours = (totalMinutes / 60).toFixed(1);

      const summaryBar = document.createElement("div");
      summaryBar.className = "card mb-3 shadow-sm";

      summaryBar.innerHTML = `
      <div class="card-body py-2">
        <div class="row text-center">
          <div class="col-md-3">
            <div class="fw-semibold">${sessions.length}</div>
            <small class="text-muted">Sessions</small>
          </div>
          <div class="col-md-3">
            <div class="fw-semibold">${totalHours}</div>
            <small class="text-muted">Planned hours</small>
          </div>
          <div class="col-md-3">
            <div class="fw-semibold">${aiUsed ? "On" : "Off"}</div>
            <small class="text-muted">AI</small>
          </div>
          <div class="col-md-3">
            <div class="fw-semibold">${warnings.length}</div>
            <small class="text-muted">Warnings</small>
          </div>
        </div>
      </div>
    `;

      scheduleView.appendChild(summaryBar);

      // Render upcoming deadlines card
      if (upcomingDeadlines.length > 0) {
        const deadlineCard = document.createElement("div");
        deadlineCard.className = "card mb-3 shadow-sm";

        deadlineCard.innerHTML = `
          <div class="card-body">
            <strong>Upcoming deadlines</strong>
            <ul class="mb-0 mt-2">
              ${upcomingDeadlines
                .slice(0, 5)
                .map((d) => {
                  let badgeClass = "bg-secondary";
                  let label = `${d.daysRemaining} days left`;

                  if (d.daysRemaining < 0) {
                    badgeClass = "bg-dark";
                    label = "Past due";
                  } else if (d.daysRemaining <= 3) {
                    badgeClass = "bg-danger";
                  } else if (d.daysRemaining <= 7) {
                    badgeClass = "bg-warning text-dark";
                  }

                  return `
                    <li class="mb-2">
                      <div class="d-flex justify-content-between align-items-start">
                        <div>
                          <div><strong>${d.title}</strong></div>
                          <small class="text-muted">${d.module} • Due ${d.deadline}</small>
                        </div>
                        <span class="badge ${badgeClass}">${label}</span>
                      </div>
                    </li>
                  `;
                })
                .join("")}
            </ul>
          </div>
        `;

        scheduleView.appendChild(deadlineCard);
      }

      // Render scheduling warnings
      if (warnings.length > 0) {
        const warningCard = document.createElement("div");
        warningCard.className = "alert alert-warning mb-3";

        warningCard.innerHTML = `
          <strong>Schedule warnings</strong>
          <ul class="mb-0 mt-2">
            ${warnings.map((w) => `<li>${w}</li>`).join("")}
          </ul>
        `;

        scheduleView.appendChild(warningCard);
      }

      // Render AI tips
      if (Array.isArray(data.ai_tips) && data.ai_tips.length > 0) {
        const tipsCard = document.createElement("div");
        tipsCard.className = "card mb-3 shadow-sm";
        tipsCard.innerHTML = `
            <div class="card-body">
            <strong>Study tips</strong>
            <ul class="mb-0">
            ${data.ai_tips
              .map(
                (t) =>
                  `<li><strong>${t.task_title ?? "Task"}</strong> (${t.module ?? "Module"}): ${t.tip}</li>`,
              )
              .join("")}
              </ul>
            </div>
          `;

        scheduleView.appendChild(tipsCard);
      }

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
      if (sessions.length === 0) {
        scheduleView.innerHTML += `
        <div class="text-center text-muted py-4">
          <div class="mb-2 fs-5">No schedule generated yet</div>
          <div class="small">
            Add modules, tasks, and availability, then click
            <strong>Generate Schedule</strong>.
          </div>
        </div>
        `;
      } else {
        const calHost = document.createElement("div");
        scheduleView.appendChild(calHost);
        renderWeeklyCalendar(calHost, sessions, {
          startHour: 6,
          endHour: 22,
        });
      }

      // logs research data
      logEvent("schedule_generated", {
        ai_enabled: aiUsed,
        ai_strictness: payload.ai_strictness,
        total_sessions: sessions.length,
        total_warnings: warnings.length,
        module_count: payload.modules.length,
        availability_count: payload.availability.length,
      });
    }

    // Restore button after successful generation
    generateBtn.disabled = false;
    generateBtn.innerHTML = `<i class="bi bi-magic me-1"></i>Generate Schedule`;
  } catch (err) {
    console.error("Fetch Failed", err);

    // Restore button if request fails
    generateBtn.disabled = false;
    generateBtn.innerHTML = `<i class="bi bi-magic me-1"></i>Generate Schedule`;

    alert("Could not reach backend. Is Flask running? " + err.message);
  }
});
