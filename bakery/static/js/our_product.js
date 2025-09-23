function attachCategoryListeners() {
    // Category radios
    document.querySelectorAll('input[name="category"]').forEach(radio => {
        radio.addEventListener('change', function () {
            const categoryId = this.value;

            const newUrl = `${window.location.pathname}?category=${encodeURIComponent(categoryId)}`;
            window.history.replaceState(null, '', newUrl);

            fetchProducts(newUrl);
        });
    });

    // Subcategory radios
    document.querySelectorAll('input[name="subcategory"]').forEach(radio => {
        radio.addEventListener('change', function () {
            const subcategoryId = this.value;

            const newUrl = `${window.location.pathname}?subcategory=${encodeURIComponent(subcategoryId)}`;
            window.history.replaceState(null, '', newUrl);

            fetchProducts(newUrl);
        });
    });
}

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
                attachCartListeners();
            } else {
                console.error("Could not find #products-container in fetched HTML");
            }
        })
        .catch(err => console.error("Fetch error:", err));
}
