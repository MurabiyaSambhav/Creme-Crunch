document.addEventListener("DOMContentLoaded", function () {

    // ===============================
    // Category / Subcategory
    // ===============================
    const categorySelect = document.getElementById("category");
    const subSelect = document.getElementById("subcategories");
    const selectedBox = document.getElementById("selected-subcategories");
    const allCategories = window.allCategories || [];

    function loadSubcategories(categoryId) {
        subSelect.innerHTML = "";
        selectedBox.innerHTML = "";
        document.querySelectorAll('.hidden-sub').forEach(el => el.remove());

        if (!categoryId) {
            subSelect.innerHTML = '<option value="">-- Select a category first --</option>';
            return;
        }

        const category = allCategories.find(c => c.id == categoryId);
        if (category && category.subcategories.length > 0) {
            category.subcategories.forEach(sub => {
                const option = document.createElement("option");
                option.value = sub.id;
                option.textContent = sub.name;
                subSelect.appendChild(option);
            });

            // Pre-select subcategories in edit mode
            if (window.preSelectedSubcategories) {
                window.preSelectedSubcategories.forEach(id => {
                    const option = Array.from(subSelect.options).find(o => o.value == id);
                    if (option) option.selected = true;
                });
            }
            subSelect.dispatchEvent(new Event('change'));
        }
    }

    function updateSelectedSubcategoriesInputs() {
        document.querySelectorAll('.hidden-sub').forEach(el => el.remove());
        Array.from(subSelect.selectedOptions).forEach(option => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'subcategories';
            input.value = option.value;
            input.classList.add('hidden-sub');
            document.querySelector('form').appendChild(input);
        });
    }

    subSelect?.addEventListener("change", function () {
        selectedBox.innerHTML = "";
        Array.from(subSelect.selectedOptions).forEach(option => {
            const tag = document.createElement("span");
            tag.classList.add("tag");
            tag.innerHTML = `${option.text} <button type="button" data-id="${option.value}" class="remove-sub">x</button>`;
            selectedBox.appendChild(tag);
        });
        updateSelectedSubcategoriesInputs();
    });

    selectedBox?.addEventListener("click", function (e) {
        if (e.target.classList.contains("remove-sub")) {
            const id = e.target.getAttribute("data-id");
            Array.from(subSelect.options).forEach(opt => {
                if (opt.value === id) opt.selected = false;
            });
            e.target.parentElement.remove();
            updateSelectedSubcategoriesInputs();
        }
    });

    categorySelect?.addEventListener("change", e => loadSubcategories(e.target.value));

    // Pre-load subcategories if category is already selected (edit mode)
    if (categorySelect?.value) loadSubcategories(categorySelect.value);

    // ===============================
    // Weights + Prices
    // ===============================
    const weightsContainer = document.getElementById("weights-container");
    if (weightsContainer) {
        weightsContainer.addEventListener("click", function (e) {
            if (e.target.classList.contains("btn-add-weight")) {
                const newGroup = document.createElement("div");
                newGroup.classList.add("weight-group");
                newGroup.innerHTML = `
                    <input type="text" name="weights[]" placeholder="Weight" required />
                    <input type="number" name="prices[]" placeholder="Price" step="0.01" required />
                    <button type="button" class="btn-add-weight">+</button>
                    <button type="button" class="btn-remove-weight">-</button>
                `;
                weightsContainer.appendChild(newGroup);
            }

            if (e.target.classList.contains("btn-remove-weight")) {
                const group = e.target.parentElement;
                if (group.dataset.existing) {
                    const hiddenInput = document.createElement("input");
                    hiddenInput.type = "hidden";
                    hiddenInput.name = "delete_weights[]";
                    hiddenInput.value = group.dataset.existing;
                    document.querySelector("form").appendChild(hiddenInput);
                }
                group.remove();
            }
        });
    }

    // ===============================
    // Images (Main + Preview + Remove)
    // ===============================
// ===============================
// Images (Main + Preview + Remove)
// ===============================
const imagesContainer = document.getElementById("images-container");
let imageIndex = imagesContainer?.querySelectorAll(".image-group").length || 0;

// Preview selected image
window.previewImage = function(input) {
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = input.parentElement.querySelector(".preview");
            img.src = e.target.result;
            img.style.display = "block";
        }
        reader.readAsDataURL(file);
    }
}

// Add new image (via separate + button)
window.addImage = function() {
    const div = document.createElement("div");
    div.classList.add("image-group");
    div.innerHTML = `
        <input type="file" name="images[]" accept="image/*" onchange="previewImage(this)" required />
        <img class="preview" style="display:none; max-width:100px; margin-top:5px;" />
        <input type="radio" name="main_image" value="${imageIndex}" /> Main
        <button type="button" class="btn-remove-image">-</button>
    `;
    imagesContainer.appendChild(div);
    imageIndex++;
}

// Handle remove image
imagesContainer?.addEventListener("click", function(e) {
    if (!e.target.classList.contains("btn-remove-image")) return;

    const imgGroup = e.target.parentElement;

    // If existing image, mark for deletion
    if (imgGroup.dataset.existing) {
        const hiddenInput = document.createElement("input");
        hiddenInput.type = "hidden";
        hiddenInput.name = "delete_images[]";
        hiddenInput.value = imgGroup.dataset.existing;
        document.querySelector("form").appendChild(hiddenInput);
    }

    // Remove from DOM
    imgGroup.remove();
});


});
