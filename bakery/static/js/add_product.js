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

function refreshCategories() {
    fetch("/get_categories/")
        .then(res => res.json())
        .then(data => {
            const select = document.getElementById('category');
            select.innerHTML = '<option value="">-- Select Category --</option>';
            data.categories.forEach(cat => {
                select.insertAdjacentHTML("beforeend",
                    `<option value="${cat.id}">${cat.name}</option>`);
            });
        });
}

function saveCategory() {
    const name = document.getElementById("new-category").value.trim();
    if (!name) return alert("Please enter a name.");

    postJSON("/add_category/", { name }).then(data => {
        if (data.success) {
            refreshCategories();
            toggleBox("category-input-box", false);
        } else {
            alert(data.error || "Error adding category.");
        }
    });
}

function loadSubcategories(categoryId) {
    const container = document.getElementById('subcategory-container');
    container.innerHTML = "";

    if (!categoryId) return;

    fetch(`/get_subcategories/${categoryId}/`)
        .then(res => res.json())
        .then(data => {
            if (data.subcategories.length > 0) {
                data.subcategories.forEach(sub => {
                    container.insertAdjacentHTML("beforeend", `
                        <label>
                            <input type="checkbox" name="subcategories" value="${sub.id}">
                            ${sub.name}
                        </label><br>
                    `);
                });
            } else {
                container.innerHTML = "<p style='color:gray;'>No subcategories found.</p>";
            }
        });
}

function saveSubcategory() {
    const parentId = document.getElementById('category').value;
    if (!parentId) return alert("Select a category first.");

    const name = document.getElementById("new-subcategory").value.trim();
    if (!name) return alert("Please enter a name.");

    postJSON("/add_subcategory/", { name, parent: parentId }).then(data => {
        if (data.success) {
            loadSubcategories(parentId);
            toggleBox("subcategory-input-box", false);
        } else {
            alert(data.error || "Error adding subcategory.");
        }
    });
}

// ---------- Image Handling ----------
function addImage() {
    const container = document.getElementById("images-container");

    const div = document.createElement("div");
    div.classList.add("image-group");

    div.innerHTML = `
        <input type="file" name="images[]" accept="image/*" required />
        <button type="button" onclick="removeImage(this)">-</button>
    `;

    container.appendChild(div);
}

function removeImage(btn) {
    btn.parentElement.remove();
}

// ---------- Weight Handling ----------
const weightsContainer = document.getElementById("weights-container");

weightsContainer.addEventListener("click", function (e) {
    if (e.target.classList.contains("btn-add-weight")) {
        const newGroup = document.createElement("div");
        newGroup.classList.add("weight-group");

        newGroup.innerHTML = `
            <input type="text" name="weights[]" placeholder="Enter weight" required />
            <button type="button" class="btn-add-weight">+</button>
            <button type="button" class="btn-remove-weight">-</button>
        `;

        weightsContainer.appendChild(newGroup);
    }

    if (e.target.classList.contains("btn-remove-weight")) {
        e.target.parentElement.remove();
    }
});

// ---------- Category & Subcategory Buttons ----------
document.getElementById("btn-add_category").addEventListener("click", () => toggleBox("category-input-box"));
document.getElementById("btn-cancel-category").addEventListener("click", () => toggleBox("category-input-box", false));
document.getElementById("btn-save-category").addEventListener("click", saveCategory);

document.getElementById("btn-add_subcategory").addEventListener("click", () => toggleBox("subcategory-input-box"));
document.getElementById("btn-cancel-subcategory").addEventListener("click", () => toggleBox("subcategory-input-box", false));
document.getElementById("btn-save-subcategory").addEventListener("click", saveSubcategory);

document.getElementById("category").addEventListener("change", e => loadSubcategories(e.target.value));
