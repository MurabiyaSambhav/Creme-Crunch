// Menu toggle
const toggleBtn = document.querySelector('.menu-toggle');
const menu = document.querySelector('.admin-menu');

if (toggleBtn && menu) {
    toggleBtn.addEventListener('click', () => {
        menu.classList.toggle('active');
    });
}

// Add / Remove subcategory inputs
const addSubcategoryBtn = document.getElementById("add-subcategory");
const subcategoryContainer = document.getElementById("subcategory-container");

// Wrap existing first input in a .subcategory-wrapper
const firstInput = subcategoryContainer.querySelector("input");
if (firstInput && !firstInput.parentElement.classList.contains("subcategory-wrapper")) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("subcategory-wrapper");
    firstInput.parentElement.insertBefore(wrapper, firstInput);
    wrapper.appendChild(firstInput);

    // Add remove button for the first input
    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.textContent = "−";
    removeBtn.classList.add("remove-subcategory");
    removeBtn.addEventListener("click", () => wrapper.remove());
    wrapper.appendChild(removeBtn);
}

if (addSubcategoryBtn && subcategoryContainer) {
    addSubcategoryBtn.addEventListener("click", () => {
        const wrapper = document.createElement("div");
        wrapper.classList.add("subcategory-wrapper");

        const input = document.createElement("input");
        input.type = "text";
        input.name = "subcategories[]";
        input.placeholder = "Subcategory name";
        input.classList.add("subcategory-input");

        const removeBtn = document.createElement("button");
        removeBtn.type = "button";
        removeBtn.textContent = "−";
        removeBtn.classList.add("remove-subcategory");
        removeBtn.addEventListener("click", () => wrapper.remove());

        wrapper.appendChild(input);
        wrapper.appendChild(removeBtn);
        subcategoryContainer.appendChild(wrapper);
    });
}
