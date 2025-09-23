// ----------------------------
// Attach listeners to category and subcategory radios
// ----------------------------
function attachCategoryListeners() {
    // Category radios
    document.querySelectorAll('input[name="category"]').forEach(radio => {
        radio.removeEventListener('change', handleCategoryChange); // Remove old listeners to avoid duplicates
        radio.addEventListener('change', handleCategoryChange);
    });

    // Subcategory radios
    document.querySelectorAll('input[name="subcategory"]').forEach(radio => {
        radio.removeEventListener('change', handleSubcategoryChange); // Remove old listeners
        radio.addEventListener('change', handleSubcategoryChange);
    });
}

// ----------------------------
// Handle category selection
// ----------------------------
function handleCategoryChange(event) {
    const categoryId = event.target.value;

    // Clear subcategory selection when changing category
    document.querySelectorAll('input[name="subcategory"]').forEach(input => input.checked = false);

    // Update URL
    const newUrl = `${window.location.pathname}?category=${encodeURIComponent(categoryId)}`;
    window.history.replaceState(null, '', newUrl);

    // Fetch products via AJAX
    fetchProducts(newUrl);
}

// ----------------------------
// Handle subcategory selection
// ----------------------------
function handleSubcategoryChange(event) {
    const subcategoryId = event.target.value;

    // Find selected category to keep it in URL
    const selectedCategory = document.querySelector('input[name="category"]:checked');
    const categoryParam = selectedCategory ? selectedCategory.value : "";

    // Build URL with both category and subcategory
    let newUrl = `${window.location.pathname}?`;
    if (categoryParam) newUrl += `category=${encodeURIComponent(categoryParam)}&`;
    newUrl += `subcategory=${encodeURIComponent(subcategoryId)}`;

    window.history.replaceState(null, '', newUrl);

    // Fetch products via AJAX
    fetchProducts(newUrl);
}

// ----------------------------
// Fetch products HTML and update DOM
// ----------------------------
function fetchProducts(url) {
    fetch(url + "&format=html")
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, "text/html");
            const container = doc.querySelector("#products-container");

            if (container) {
                document.getElementById("products-container").innerHTML = container.innerHTML;

                // Reattach listeners after re-render
                attachCategoryListeners();
                attachCartListeners(); // Assuming you have a function to attach cart buttons
            } else {
                console.error("Could not find #products-container in fetched HTML");
            }
        })
        .catch(err => console.error("Fetch error:", err));
}

// ----------------------------
// Initialize on page load
// ----------------------------
document.addEventListener('DOMContentLoaded', () => {
    attachCategoryListeners();
});
