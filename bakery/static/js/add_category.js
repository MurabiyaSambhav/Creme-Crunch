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

if (addSubcategoryBtn && subcategoryContainer) {
    addSubcategoryBtn.addEventListener("click", () => {
        // Create a wrapper div for input + remove button
        const wrapper = document.createElement("div");
        wrapper.classList.add("subcategory-wrapper");

        // Create input
        const input = document.createElement("input");
        input.type = "text";
        input.name = "subcategories[]";
        input.placeholder = "Subcategory name";
        input.classList.add("subcategory-input");

        // Create remove button
        const removeBtn = document.createElement("button");
        removeBtn.type = "button";
        removeBtn.textContent = "−";
        removeBtn.classList.add("remove-subcategory");

        // Remove functionality
        removeBtn.addEventListener("click", () => {
            wrapper.remove();
        });

        // Append input + button to wrapper, then wrapper to container
        wrapper.appendChild(input);
        wrapper.appendChild(removeBtn);
        subcategoryContainer.appendChild(wrapper);
    });
}
