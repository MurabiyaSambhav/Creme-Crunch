document.addEventListener("DOMContentLoaded", function () {

    // ===============================
    // Category / Subcategory
    // ===============================
    const categorySelect = document.getElementById("category");
    const subSelect = document.getElementById("subcategories");
    const selectedBox = document.getElementById("selected-subcategories");

    function loadSubcategories(categoryId) {
        if (!subSelect) return;
        subSelect.innerHTML = ""; // reset
        if (!categoryId) {
            subSelect.innerHTML = '<option value="">-- Select a category first --</option>';
            selectedBox.innerHTML = "";
            return;
        }
        fetch(`/get_subcategories/${categoryId}/`)
            .then(res => res.json())
            .then(data => {
                if (data.subcategories.length > 0) {
                    data.subcategories.forEach(sub => {
                        subSelect.insertAdjacentHTML("beforeend",
                            `<option value="${sub.id}">${sub.name}</option>`);
                    });
                } else {
                    subSelect.innerHTML = '<option value="">-- No subcategories available --</option>';
                }
                selectedBox.innerHTML = "";
            })
            .catch(err => {
                console.error("Error loading subcategories:", err);
                subSelect.innerHTML = '<option value="">-- Error loading subcategories --</option>';
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
        });

        selectedBox.addEventListener("click", function (e) {
            if (e.target.classList.contains("remove-sub")) {
                const id = e.target.getAttribute("data-id");
                Array.from(subSelect.options).forEach(opt => {
                    if (opt.value === id) opt.selected = false;
                });
                e.target.parentElement.remove();
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
    let imageIndex = 1;
    const imagesContainer = document.getElementById("images-container");

    window.previewImage = function (input) {
        const file = input.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                let img = input.parentElement.querySelector(".preview");
                img.src = e.target.result;
                img.style.display = "block";
            }
            reader.readAsDataURL(file);
        }
    }

    window.addImage = function () {
        if (!imagesContainer) return;
        const div = document.createElement("div");
        div.classList.add("image-group");
        div.innerHTML = `
            <input type="file" name="images[]" accept="image/*" onchange="previewImage(this)" required />
            <img class="preview" style="display:none; max-width:100px; margin-top:5px;" />
            <input type="radio" name="main_image" value="${imageIndex}" ${imageIndex === 1 ? "checked" : ""}/> Main
            <button type="button" class="btn-remove-image">-</button>
        `;
        imagesContainer.appendChild(div);
        imageIndex++;
    }

    window.removeImage = function (btn) {
        btn.parentElement.remove();
    }

    imagesContainer?.addEventListener("click", function (e) {
        if (e.target.classList.contains("btn-remove-image")) removeImage(e.target);
    });

});
