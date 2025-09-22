function attachCategoryListeners() {
    document.querySelectorAll('input[name="category"]').forEach(radio => {
        radio.addEventListener('change', function () {
            const categoryName = this.value;

            // Update browser URL without reload
            const newUrl = `${window.location.pathname}?category=${encodeURIComponent(categoryName)}`;
            window.history.replaceState(null, '', newUrl);

            // Fetch filtered products
            fetch(`${window.location.pathname}?category=${encodeURIComponent(categoryName)}&format=html`)
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, "text/html");
                    const container = doc.querySelector("#products-container");

                    if (container) {
                        document.getElementById("products-container").innerHTML = container.innerHTML;

                        // Reattach listeners for new elements
                        attachCategoryListeners();
                        attachCartListeners();
                    } else {
                        console.error("Could not find #products-container in fetched HTML");
                    }
                })
                .catch(err => console.error("Fetch error:", err));
        });
    });
}

function attachCartListeners() {
    document.querySelectorAll('.add-cart-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const productId = this.dataset.product;
            // Redirect to add_cart.html page
            window.location.href = `/add_cart/?product_id=${productId}`;
        });
    });
}

// Initial call
document.addEventListener("DOMContentLoaded", () => {
    attachCategoryListeners();
    attachCartListeners();
});
