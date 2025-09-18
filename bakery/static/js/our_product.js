function attachListeners() {
    document.querySelectorAll('input[name="category"]').forEach(radio => {
        radio.addEventListener('change', function () {
            let categoryId = this.value;
            fetch(`${window.location.pathname}?category=${categoryId}&format=html`)
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, "text/html");

                    const container = doc.querySelector("#products-container");
                    if (container) {
                        document.getElementById("products-container").innerHTML = container.innerHTML;
                        attachListeners(); // reattach listeners on new elements
                    } else {
                        console.error("Could not find #products-container in fetched HTML");
                    }
                })
                .catch(err => console.error("Fetch error:", err));
        });
    });
}

document.addEventListener("DOMContentLoaded", attachListeners);
