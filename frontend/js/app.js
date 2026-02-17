const modulesContainer = document.getElementById("modulesContainer");
const addModuleBtn = document.getElementById("addModuleBtn");
const availabilityContainer = document.getElementById("availabilityContainer");
const addAvailabilityBtn = document.getElementById("addAvailabilityBtn");

// Function to create a new module input form
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

// Functions to get modules from the index page for schedule generation
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

// funcitons to get availability slots from the index page for schedule generation
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

// Form Validation (basic example, can be expanded)
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

// Generate button test

const generateBtn = document.getElementById("generateBtn");

generateBtn.addEventListener("click", async () => {
  const error = validateForm();
  if (error) {
    alert(error); // Simple for now
    return;
  }

  const payload = {
    modules: getModules(),
    availability: getAvailabilitySlots(),
    ai_enabled: document.getElementById("aiEnabled").value,
  };

  const response = await fetch("http://127.0.0.1:5000/schedule", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const result = await response.json();

  console.log(result);
});

const modules = getModules();
const availability = getAvailabilitySlots();

console.log("Modules:", modules);
console.log("Availability:", availability);

// Later: call Flask here
