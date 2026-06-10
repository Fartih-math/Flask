/* ========== borrow_equipment.html ========== */

function adjustQuantity(equipId, delta) {
    const input = document.getElementById('qty_' + equipId);
    let val = parseInt(input.value) || 0;
    const max = parseInt(input.getAttribute('data-max'));
    val = Math.min(max, Math.max(0, val + delta));
    input.value = val;
    updateBorrowButton(equipId, val);
}

function updateBorrowButton(equipId, qty) {
    const btnContainer = document.getElementById('btn_' + equipId);
    if (qty > 0) {
        btnContainer.innerHTML = `<span class="quantity-control">
        <button type="button" onclick="adjustQuantity(${equipId}, -1)">-</button>
        <input type="number" id="qty_${equipId}" data-max="${maxQty}" value="${qty}" style="width:50px; text-align:center;" readonly>
        <button type="button" onclick="adjustQuantity(${equipId}, 1)">+</button>
        </span>`;
    } else {
        btnContainer.innerHTML = `<button type="button" onclick="startBorrow(${equipId})">Borrow</button>`;
    }
}

function startBorrow(equipId) {
    const maxQty = parseInt(document.getElementById('max_' + equipId).innerText);
    const btnContainer = document.getElementById('btn_' + equipId);
    btnContainer.innerHTML = `<span class="quantity-control">
    <button type="button" onclick="adjustQuantity(${equipId}, -1)">-</button>
    <input type="number" id="qty_${equipId}" data-max="${maxQty}" value="1" style="width:50px; text-align:center;" readonly>
    <button type="button" onclick="adjustQuantity(${equipId}, 1)">+</button>
    </span>`;
}

function collectCart() {
    const items = [];
    document.querySelectorAll('.qty-input').forEach(input => {
        const qty = parseInt(input.value);
        if (qty > 0) {
            const equipId = input.id.split('_')[1];
            items.push({ equipment_id: equipId, quantity: qty });
        }
    });
    fetch('/update_cart', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({cart: items})
    }).then(res => res.json()).then(data => {
        if (data.success) window.location.href = '/cart';
        else alert('Error updating cart');
    });
}

/* ========== admin_scan_qr.html (camera & QR scanning) ========== */
// (camera and QR scan functions would go here if moved to script.js)
