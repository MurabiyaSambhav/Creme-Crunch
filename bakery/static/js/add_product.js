document.addEventListener("DOMContentLoaded", function () {
    // ===============================
    // CSRF helper
    // ===============================
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            for (const cookie of document.cookie.split(';')) {
                const trimmed = cookie.trim();
                if (trimmed.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    function postJSON(url, data) {
        return fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify(data)
        }).then(res => res.json());
    }

    // ===============================
    // Toggle Input Boxes
    // ===============================
    function toggleBox(id, show = true) {
        const el = document.getElementById(id);
        if (el) {
            el.style.display = show ? "flex" : "none";
            if (!show) {
                const input = el.querySelector("input");
                if (input) input.value = "";
            }
        }
    }

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
                selectedBox.innerHTML = ""; // clear selected tags
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
                    <input type="number" name="weight_prices[]" placeholder="Price (₹)" step="0.01" required />
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
    // Images (Main + Sub)
    // ===============================
    let imageIndex = 1;
    const imagesContainer = document.getElementById("images-container");

    window.addImage = function () {
        if (!imagesContainer) return;

        const div = document.createElement("div");
        div.classList.add("image-group");
        div.innerHTML = `
            <input type="file" name="images[]" accept="image/*" required />
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
