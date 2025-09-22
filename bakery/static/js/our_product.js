function attachListeners() {
    document.querySelectorAll('input[name="category"]').forEach(radio => {
        radio.addEventListener('change', function () {
            let categoryName = this.value; 

            
            let urlCategory = categoryName.replace(/\s+/g, '_'); 

            // Update the browser URL without reloading
            const newUrl = `${window.location.pathname}?category=${urlCategory}`;
            window.history.replaceState(null, '', newUrl);

            // Fetch filtered products using the original category name
            fetch(`${window.location.pathname}?category=${encodeURIComponent(categoryName)}&format=html`)
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, "text/html");

                    const container = doc.querySelector("#products-container");
                    if (container) {
                        document.getElementById("products-container").innerHTML = container.innerHTML;

                        // Reattach listeners to new elements
                        attachListeners();
                    } else {
                        console.error("Could not find #products-container in fetched HTML");
                    }
                })
                .catch(err => console.error("Fetch error:", err));
        });
    });
}

// Initial call
document.addEventListener("DOMContentLoaded", attachListeners);
