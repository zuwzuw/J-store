console.log("Scripts loaded...");

document.addEventListener('DOMContentLoaded', () => {
    const cartTable = document.getElementById('cart-table');
    const cartTotal = document.getElementById('cart-total');

    if (!cartTable) return;

    async function postJSON(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    }

    cartTable.addEventListener('click', async (e) => {
        const button = e.target;
        const row = button.closest('tr[data-cart-item-id]');
        if (!row) return;
        const cartItemId = row.getAttribute('data-cart-item-id');

        if (button.classList.contains('quantity-increase')) {
            let currentQty = parseInt(row.querySelector('.quantity-value').textContent, 10);
            currentQty += 1;
            const result = await postJSON(updateQuantityUrl, { cart_item_id: cartItemId, quantity: currentQty });
            if (result.success) {
                updateRow(row, currentQty, result.item_total);
                updateTotal(result.total);
            }
        }

        if (button.classList.contains('quantity-decrease')) {
            let currentQty = parseInt(row.querySelector('.quantity-value').textContent, 10);
            if (currentQty > 1) {
                currentQty -= 1;
                const result = await postJSON(updateQuantityUrl, { cart_item_id: cartItemId, quantity: currentQty });
                if (result.success) {
                    updateRow(row, currentQty, result.item_total);
                    updateTotal(result.total);
                }
            }
        }

        if (button.classList.contains('remove-item')) {
            const result = await postJSON(removeItemUrl, { cart_item_id: cartItemId });
            if (result.success) {
                row.remove();
                updateTotal(result.total);
            }
        }
    });

    function updateRow(row, newQuantity, newItemTotal) {
        row.querySelector('.quantity-value').textContent = newQuantity;
        row.querySelector('.item-total').textContent = newItemTotal;
    }

    function updateTotal(newTotal) {
        cartTotal.textContent = newTotal;
    }
});
