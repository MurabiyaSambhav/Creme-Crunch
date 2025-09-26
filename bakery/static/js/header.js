// ------------------ SEARCH SUGGESTIONS ------------------
const searchInput = document.getElementById('search-input');
const suggestionsBox = document.getElementById('suggestions');
let debounceTimeout = null;
let selectedIndex = -1;

searchInput.addEventListener('input', function () {
    const query = this.value.trim();
    clearTimeout(debounceTimeout);

    if (!query) {
        hideSuggestions();
        return;
    }

    debounceTimeout = setTimeout(() => {
        fetch(`/product-suggestions/?q=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => renderSuggestions(data.results))
            .catch(err => {
                console.error("Suggestion fetch error:", err);
                hideSuggestions();
            });
    }, 300);
});

function renderSuggestions(results) {
    suggestionsBox.innerHTML = '';
    selectedIndex = -1;

    if (!results || results.length === 0) {
        hideSuggestions();
        return;
    }

    suggestionsBox.style.display = 'block';
    results.forEach((item) => {
        const div = document.createElement('div');
        div.textContent = `${item.name} (${item.category})`;
        div.dataset.categoryId = item.category_id || '';

        div.addEventListener('click', () => selectSuggestion(item, div.dataset.categoryId));

        suggestionsBox.appendChild(div);
    });
}

function selectSuggestion(item, categoryId) {
    searchInput.value = item.name;

    // Set hidden category input
    let categoryInput = document.querySelector('#search-form input[name="category"]');
    if (!categoryInput) {
        categoryInput = document.createElement('input');
        categoryInput.type = 'hidden';
        categoryInput.name = 'category';
        document.getElementById('search-form').appendChild(categoryInput);
    }
    categoryInput.value = categoryId;

    document.getElementById('search-form').submit();
}

function hideSuggestions() {
    suggestionsBox.innerHTML = '';
    suggestionsBox.style.display = 'none';
}

// ------------------ KEYBOARD NAVIGATION ------------------
searchInput.addEventListener('keydown', function (e) {
    const items = suggestionsBox.querySelectorAll('div');
    if (items.length === 0) return;

    if (e.key === "ArrowDown") {
        e.preventDefault();
        selectedIndex = (selectedIndex + 1) % items.length;
        updateSelection(items);
    } else if (e.key === "ArrowUp") {
        e.preventDefault();
        selectedIndex = (selectedIndex - 1 + items.length) % items.length;
        updateSelection(items);
    } else if (e.key === "Enter") {
        if (selectedIndex >= 0 && items[selectedIndex]) {
            e.preventDefault();
            items[selectedIndex].click();
        }
    }
});

function updateSelection(items) {
    items.forEach((item, idx) => {
        item.style.background = idx === selectedIndex ? "#f0f0f0" : "";
    });
}

// ------------------ CLOSE SUGGESTIONS ON OUTSIDE CLICK ------------------
document.addEventListener('click', function (e) {
    if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
        hideSuggestions();
    }
});

// ------------------ MOBILE MENU TOGGLE ------------------
const menuToggle = document.querySelector('.menu-toggle');
const navMenu = document.querySelector('.nav-menu');

if (menuToggle && navMenu) {
    menuToggle.addEventListener('click', () => {
        navMenu.style.display = navMenu.style.display === 'flex' ? 'none' : 'flex';
    });
}
