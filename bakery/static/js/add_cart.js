document.addEventListener("DOMContentLoaded", () => {
    const quantityInput = document.getElementById("quantity");
    const decreaseBtn = document.getElementById("decrease");
    const increaseBtn = document.getElementById("increase");
    const weightSelect = document.getElementById("weight");
    const priceSpan = document.getElementById("price");
    const addToCartBtn = document.getElementById('add-to-cart');

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const addCartUrl = window.addCartConfig.url;
    const productId = window.addCartConfig.productId;

    // Thumbnail click
    document.querySelectorAll('.thumb-img').forEach(img => {
        img.addEventListener('click', () => {
            document.getElementById('main-img').src = img.src;
        });
    });

    // Quantity buttons
    decreaseBtn.addEventListener("click", () => {
        let qty = parseInt(quantityInput.value);
        if (qty > 1) quantityInput.value = qty - 1;
    });
    increaseBtn.addEventListener("click", () => {
        let qty = parseInt(quantityInput.value);
        quantityInput.value = qty + 1;
    });

    // Weight price update
    weightSelect.addEventListener("change", () => {
        const selectedOption = weightSelect.options[weightSelect.selectedIndex];
        const newPrice = selectedOption.getAttribute("data-price");
        priceSpan.textContent = `₹${parseFloat(newPrice).toFixed(2)}`;
    });

    // Add to cart
    addToCartBtn.addEventListener('click', async () => {
        const weightId = weightSelect.value;
        const quantity = quantityInput.value;

        try {
            const response = await fetch(addCartUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ product_id: productId, weight_id: weightId, quantity: quantity })
            });

            let data;
            try {
                data = await response.json();
            } catch (err) {
                const text = await response.text();
                console.error("Server returned non-JSON response:", text);
                alert("Something went wrong. Server did not return JSON.");
                return;
            }

            if (data.status === 'success') {
                alert(data.message);
            } else {
                alert(data.message || "Failed to add to cart.");
            }

        } catch (error) {
            console.error('Error adding to cart:', error);
            alert('Something went wrong. Please try again.');
        }
    });
});
