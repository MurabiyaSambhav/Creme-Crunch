document.addEventListener("DOMContentLoaded", function () {

    // ===============================
    // Category / Subcategory
    // ===============================
    const categorySelect = document.getElementById("category");
    const subSelect = document.getElementById("subcategories");
    const selectedBox = document.getElementById("selected-subcategories");

    const allCategories = window.allCategories || [];
    // Format: [{id, name, subcategories:[{id, name}, ...]}, ...]

    function loadSubcategories(categoryId) {
        if (!subSelect) return;

        subSelect.innerHTML = ""; // reset
        selectedBox.innerHTML = ""; // clear selected tags
        document.querySelectorAll('.hidden-sub').forEach(el => el.remove()); // clear old hidden inputs

        if (!categoryId) {
            subSelect.innerHTML = '<option value="">-- Select a category first --</option>';
            return;
        }

        const category = allCategories.find(cat => cat.id === parseInt(categoryId));
        if (category && category.subcategories.length > 0) {
            category.subcategories.forEach(sub => {
                const option = document.createElement("option");
                option.value = sub.id;
                option.textContent = sub.name;
                subSelect.appendChild(option);
            });
        } else {
            subSelect.innerHTML = '<option value="">-- No subcategories available --</option>';
        }
    }

    function updateSelectedSubcategoriesInputs() {
        document.querySelectorAll('.hidden-sub').forEach(el => el.remove());
        if (!subSelect) return;

        Array.from(subSelect.selectedOptions).forEach(option => {
            if (option.value) {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'subcategories'; // backend receives list of IDs
                input.value = option.value;
                input.classList.add('hidden-sub');
                document.querySelector('form').appendChild(input);
            }
        });
    }

    if (subSelect && selectedBox) {
        subSelect.addEventListener("change", function () {
            selectedBox.innerHTML = "";
            Array.from(subSelect.selectedOptions).forEach(option => {
                const tag = document.createElement("span");
                tag.classList.add("tag");
                tag.innerHTML = `${option.text} <button type="button" data-id="${option.value}" class="remove-sub">x</button>`;
                selectedBox.appendChild(tag);
            });
            updateSelectedSubcategoriesInputs();
        });

        selectedBox.addEventListener("click", function (e) {
            if (e.target.classList.contains("remove-sub")) {
                const id = e.target.getAttribute("data-id");
                Array.from(subSelect.options).forEach(opt => {
                    if (opt.value === id) opt.selected = false;
                });
                e.target.parentElement.remove();
                updateSelectedSubcategoriesInputs();
            }
        });
    }

    categorySelect?.addEventListener("change", e => loadSubcategories(e.target.value));

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
                    <input type="text" name="weights[]" placeholder="Weight (e.g. 250g, 1kg)" required />
                    <input type="number" name="prices[]" placeholder="Price (₹)" step="0.01" required />
                    <button type="button" class="btn-add-weight">+</button>
                    <button type="button" class="btn-remove-weight">-</button>
                `;
                weightsContainer.appendChild(newGroup);
            }
            if (e.target.classList.contains("btn-remove-weight")) {
                e.target.parentElement.remove();
            }
        });
    }

    // ===============================
    // Images (Main + Preview + Remove)
    // ===============================
    let imageIndex = 0; // first image is 0
    const imagesContainer = document.getElementById("images-container");

    window.previewImage = function (input) {
        const file = input.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const img = input.parentElement.querySelector(".preview");
                img.src = e.target.result;
                img.style.display = "block";
            }
            reader.readAsDataURL(file);
        }
    }

    window.addImage = function () {
        if (!imagesContainer) return;
        imageIndex++;
        const div = document.createElement("div");
        div.classList.add("image-group");
        div.innerHTML = `
            <input type="file" name="images[]" accept="image/*" onchange="previewImage(this)" required />
            <img class="preview" style="display:none; max-width:100px; margin-top:5px;" />
            <input type="radio" name="main_image" value="${imageIndex}" /> Main
            <button type="button" class="btn-remove-image">-</button>
        `;
        imagesContainer.appendChild(div);
    }

    window.removeImage = function (btn) {
        btn.parentElement.remove();
    }

    imagesContainer?.addEventListener("click", function (e) {
        if (e.target.classList.contains("btn-remove-image")) removeImage(e.target);
    });

});
