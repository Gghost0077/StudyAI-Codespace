const modulesContainer = document.getElementById("modulesContainer");
const addModuleBtn = document.getElementById("addModuleBtn");

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

        <button class="btn btn-sm btn-outline-danger removeModuleBtn">Remove Module</button>
         Remove
        </button>

    `;

  modulesContainer.appendChild(moduleDiv);

  // add remove functionality to the remove button
  moduleDiv.querySelector(".removeModuleBtn").addEventListener("click", () => {
    moduleDiv.remove();
  });
}

createModuleBlock(); // Create the first module input block on page load

addModuleBtn.addEventListener("click", createModuleBlock);
