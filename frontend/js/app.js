const modulesContainer = document.getElementById("modulesContainer");
const addModuleBtn = document.getElementById("addModuleBtn");
const availabilityContainer = document.getElementById("availabilityContainer");
const addAvailabilityBtn = document.getElementById("addAvailabilityBtn");

// Function to create a new module input form
function createModuleBlock() {
  const moduleDiv = document.createElement("div");
  moduleDiv.classList.add("border", "p-3", "mb-3", "rounded");

  moduleDiv.innerHTML = `
        <div class="mb-2">
         <label class="form-label">Module Name</label>
         <input type="text" class="form-control module-name" placeholder="Enter module name"/>
        </div>

        <div class="mb-2">
        <label class="form-label">Importance</label>
        <select class="form-select module-importance">
            <option value="1">1 (LOW)</option>
            <option value="2" selected>2 (MEDIUM)</option>
            <option value="3">3 (HIGH)</option>
        </select>
        </div>

        <div class="mb-2">
         <label class="form-label">Module Deadline</label>
         <input type="date" class="form-control module-deadline"/>
        </div>

        <button class="btn btn-sm btn-outline-danger removeModuleBtn">Remove Module</button>
         Remove
        </button>

    `;

  function createAvailabilityBlock() {
    const slot = document.createElement("div");
    slot.classList.add("border", "p-3", "mb-3", "rounded");

    slot.innerHTML = `
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

    <div class="row g-2 mb-2">
    <div class="col-6">
    <label class="form-label">Start Time</label>
    <input type="time" class="form-control availability-start"/>
    </div>
    <div class="col-6">
    <label class="form-label">End Time</label>
    <input type="time" class="form-control availability-end"/>
    </div>
    </div>

    <button class="btn btn-sm btn-outline-danger removeAvailabilityBtn">Remove Slot</button>

  `;

    availabilityContainer.appendChild(slot); // add remove button functionality
    slot
      .querySelector(".removeAvailabilityBtn")
      .addEventListener("click", () => {
        slot.remove();
      });
  }

  createAvailabilityBlock(); // Create the first availability input block on page load

  addAvailabilityBtn.addEventListener("click", createAvailabilityBlock);

  modulesContainer.appendChild(moduleDiv);

  // add remove functionality to the remove button
  moduleDiv.querySelector(".removeModuleBtn").addEventListener("click", () => {
    moduleDiv.remove();
  });
}

createModuleBlock(); // Create the first module input block on page load

addModuleBtn.addEventListener("click", createModuleBlock);
