document.addEventListener('DOMContentLoaded', () => {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    // Function to update quantity
    function updateQuantity(row, quantity) {
        const productId = row.dataset.product;
        const weightId = row.dataset.weight;

        fetch('/update_cart/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `product_id=${productId}&weight_id=${weightId}&quantity=${quantity}`
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Update the row item total
                row.querySelector('.item-total').textContent = `₹${data.item_total}`;

                // Update subtotal & total in both columns
                document.getElementById('cart-subtotal').textContent = data.subtotal;
                document.getElementById('cart-total').textContent = data.subtotal;

                // Update the quantity input value
                row.querySelector('.quantity').value = quantity;

                // Update "Your Order" right column table
                updateOrderSummary();
            }
        });
    }

    // Function to remove row
    function removeItem(row) {
        const productId = row.dataset.product;
        const weightId = row.dataset.weight;

        fetch('/remove_cart_item/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `product_id=${productId}&weight_id=${weightId}`
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                row.remove(); // Remove the row from cart table
                document.getElementById('cart-subtotal').textContent = data.subtotal;
                document.getElementById('cart-total').textContent = data.subtotal;

                // Update right column "Your Order"
                updateOrderSummary();
            }
        });
    }

    // Update "Your Order" table dynamically
    function updateOrderSummary() {
        const orderTableBody = document.querySelector('.order-summary-table tbody');
        orderTableBody.innerHTML = ''; // Clear existing rows

        document.querySelectorAll('.cart-table tbody tr').forEach(row => {
            const name = row.querySelector('td:nth-child(2)').innerText;
            const total = row.querySelector('.item-total').innerText;

            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${name}</td><td style="text-align:right;">${total}</td>`;
            orderTableBody.appendChild(tr);
        });
    }

    // Event delegation for dynamic updates
    document.querySelector('.cart-column').addEventListener('click', e => {
        const row = e.target.closest('tr');
        if (!row) return;

        if (e.target.classList.contains('increase')) {
            let qty = parseInt(row.querySelector('.quantity').value);
            updateQuantity(row, qty + 1);
        }

        if (e.target.classList.contains('decrease')) {
            let qty = parseInt(row.querySelector('.quantity').value);
            if (qty > 1) updateQuantity(row, qty - 1);
        }

        if (e.target.classList.contains('remove-item')) {
            removeItem(row);
        }
    });
});
