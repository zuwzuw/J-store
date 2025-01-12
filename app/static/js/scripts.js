console.log("Scripts loaded...");

document.addEventListener('DOMContentLoaded', () => {
    const cartTable = document.getElementById('cart-table');
    const cartTotal = document.getElementById('cart-total');

    // Проверка существования таблицы корзины
    if (cartTable) {
        cartTable.addEventListener('click', handleCartActions);
    }

    // Функция для отправки POST-запросов с JSON
    async function postJSON(url, data) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error("Error posting JSON:", error);
            return { success: false };
        }
    }

    // Обработчик событий для таблицы корзины
    async function handleCartActions(e) {
        const button = e.target;
        const row = button.closest('tr[data-cart-item-id]');
        if (!row) return;

        const cartItemId = row.getAttribute('data-cart-item-id');

        // Увеличение количества
        if (button.classList.contains('quantity-increase')) {
            await updateQuantity(row, cartItemId, 1);
        }

        // Уменьшение количества
        if (button.classList.contains('quantity-decrease')) {
            await updateQuantity(row, cartItemId, -1);
        }

        // Удаление элемента из корзины
        if (button.classList.contains('remove-item')) {
            await removeCartItem(row, cartItemId);
        }
    }

    // Функция обновления количества
    async function updateQuantity(row, cartItemId, delta) {
        const quantityElement = row.querySelector('.quantity-value');
        let currentQty = parseInt(quantityElement.textContent, 10);

        if (currentQty + delta < 1) return;

        const newQuantity = currentQty + delta;
        const result = await postJSON(updateQuantityUrl, { cart_item_id: cartItemId, quantity: newQuantity });

        if (result.success) {
            updateRow(row, newQuantity, result.item_total);
            updateTotal(result.total);
        }
    }

    // Функция удаления элемента из корзины
    async function removeCartItem(row, cartItemId) {
        const result = await postJSON(removeItemUrl, { cart_item_id: cartItemId });

        if (result.success) {
            row.remove();
            updateTotal(result.total);
        }
    }

    // Обновление строки в таблице корзины
    function updateRow(row, newQuantity, newItemTotal) {
        row.querySelector('.quantity-value').textContent = newQuantity;
        row.querySelector('.item-total').textContent = newItemTotal;
    }

    // Обновление общего итога корзины
    function updateTotal(newTotal) {
        cartTotal.textContent = newTotal;
    }

    // Превью изображения
    const fileInput = document.getElementById('product-image');
    if (fileInput) {
        fileInput.addEventListener('change', previewImage);
    }

    function previewImage(event) {
        const preview = document.getElementById('image-preview');
        const file = event.target.files[0]; // Получаем выбранный файл
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                preview.src = e.target.result; // Устанавливаем результат как src изображения
                preview.style.display = 'block'; // Показываем изображение
            };
            reader.readAsDataURL(file); // Читаем файл как Data URL
        } else {
            preview.src = '#';
            preview.style.display = 'none'; // Прячем превью, если файл не выбран
        }
    }
});
