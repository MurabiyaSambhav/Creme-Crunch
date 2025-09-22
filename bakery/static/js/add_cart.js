document.addEventListener("DOMContentLoaded", () => {

    // Change main image on thumbnail click
    document.querySelectorAll('.thumb-img').forEach(img => {
        img.addEventListener('click', function () {
            document.getElementById('main-img').src = this.src;
        });
    });

    // Update price dynamically
    function updatePrice() {
        const qty = parseInt(document.getElementById('quantity').value);
        const weightSelect = document.getElementById('weight');
        const weightPrice = parseFloat(weightSelect.selectedOptions[0].dataset.price);
        document.getElementById('price').textContent = `₹${(qty * weightPrice).toFixed(2)}`;
    }

    // Update on page load
    updatePrice();

    // Update price when weight or quantity changes
    document.getElementById('weight').addEventListener('change', updatePrice);
    document.getElementById('quantity').addEventListener('input', updatePrice);

    // Optional: buttons to increase/decrease quantity
    window.changeQuantity = function (val) {
        let qtyInput = document.getElementById('quantity');
        let qty = parseInt(qtyInput.value) + val;
        if (qty < 1) qty = 1;
        qtyInput.value = qty;
        updatePrice();
    };

    // Add to cart button using AJAX POST (URL stays clean)
    document.getElementById('add-to-cart').addEventListener('click', function () {
        const weightId = document.getElementById('weight').value;
        const quantity = document.getElementById('quantity').value;
        const productId = "{{ product.id }}"; // passed from template

        fetch('/add_cart/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify({
                product_id: productId,
                weight_id: weightId,
                quantity: quantity
            })
        })
            .then(response => response.json())
            .then(data => {
                // Optionally show a success message or update cart count
                alert('Product added to cart!');
            })
            .catch(error => {
                console.error('Error adding to cart:', error);
            });
    });

});
    