const searchInput = document.getElementById('search-input');
const suggestionsBox = document.getElementById('suggestions');

let debounceTimeout = null;
let selectedIndex = -1;

searchInput.addEventListener('input', function () {
    const query = this.value.trim();

    clearTimeout(debounceTimeout);

    if (!query) {
        suggestionsBox.innerHTML = '';
        suggestionsBox.style.display = "none";
        return;
    }

    debounceTimeout = setTimeout(() => {
        fetch(`/product-suggestions/?q=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => {
                suggestionsBox.innerHTML = '';
                selectedIndex = -1; // reset selection

                if (data.results.length > 0) {
                    suggestionsBox.style.display = "block";
                    data.results.forEach((item, index) => {
                        const div = document.createElement('div');
                        div.textContent = `${item.name} (${item.category})`;

                        div.addEventListener('click', () => {
                            searchInput.value = item.name;
                            document.getElementById('search-form').submit();
                        });

                        suggestionsBox.appendChild(div);
                    });
                } else {
                    suggestionsBox.style.display = "none";
                }
            })
            .catch(err => {
                console.error("Suggestion fetch error:", err);
                suggestionsBox.style.display = "none";
            });
    }, 300); // debounce 300ms
});

// Keyboard navigation for suggestions
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

// Close suggestions when clicking outside
document.addEventListener('click', function (e) {
    if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
        suggestionsBox.innerHTML = '';
        suggestionsBox.style.display = "none";
    }
});

// MOBILE MENU TOGGLE
const menuToggle = document.querySelector('.menu-toggle');
const navMenu = document.querySelector('.nav-menu');
menuToggle.addEventListener('click', () => {
    navMenu.style.display = navMenu.style.display === 'flex' ? 'none' : 'flex';
});
