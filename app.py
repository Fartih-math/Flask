from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, get_flashed_messages
from models import db, User, Equipment, BorrowSession, BorrowItem
from encryption_utils import encrypt_name, decrypt_name
from qr_utils import generate_qr_code_base64
from datetime import datetime, timedelta
import secrets
import os

app = Flask(__name__)
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///equipment.db'
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
db.init_app(app)

translations = {
    # index.html:
    "Equipment Loan Tracker": {"en": "Equipment Loan Tracker", "id": "Pelacak Pinjaman Peralatan"},
    "Borrow & Return with QR Security": {"en": "Borrow & Return with QR Security", "id": "Pinjam & Kembalikan dengan Keamanan QR"},
    "Login as Customer": {"en": "Login as Customer", "id": "Masuk sebagai Pelanggan"},
    "Login as Admin": {"en": "Login as Admin", "id": "Masuk sebagai Admin"},
    "Don't have an account? Register here": {"en": "Don't have an account? Register here", "id": "Tidak punya akun? Daftar di sini"},
    # login customer:
    "Login": {"en": "Login", "id": "Masuk"},
    "Access your account": {"en": "Access your account", "id": "Akses akun anda"},
    "Username": {"en": "Username", "id": "Nama Pengguna"},
    "Password": {"en": "Password", "id": "Kata Sandi"},
    "Login": {"en": "Login", "id": "Masuk"},
    # Admin_Login.html:
    "Admin Login": {"en": "Admin Login", "id": "Masuk Admin"},
    "Access the administration panel": {"en": "Access the administration panel", "id": "Akses panel administrasi"},
    "Username": {"en": "Username", "id": "Nama Pengguna"},
    "Password": {"en": "Password", "id": "Kata Sandi"},
    "Login as Admin": {"en": "Login as Admin", "id": "Masuk sebagai Admin"},
    # Register.html:
    "Register": {"en": "Register", "id": "Daftar"},
    "Create a new account": {"en": "Create a new account", "id": "Buat akun baru"},
    "Username": {"en": "Username", "id": "Nama Pengguna"},
    "Password": {"en": "Password", "id": "Kata Sandi"},
    "Full Name": {"en": "Full Name", "id": "Nama Lengkap"},
    "Customer": {"en": "Customer", "id": "Pelanggan"},
    "Admin": {"en": "Admin", "id": "Admin"},
    # Customer Dashboard:
    "Welcome back": {"en": "Welcome back", "id": "Selamat datang kembali"},
    "Borrow Equipment": {"en": "Borrow Equipment", "id": "Pinjam Peralatan"},
    "My Loans": {"en": "My Loans", "id": "Pinjaman Saya"},
    "Profile": {"en": "Profile", "id": "Profil"},
    "Logout": {"en": "Logout", "id": "Keluar"},
    "Here's how to borrow equipment and manage your loans": {"en": "Here's how to borrow equipment and manage your loans", "id": "Berikut cara meminjam peralatan dan mengelola pinjaman Anda"},
    "Browse": {"en": "Browse", "id": "Jelajahi"},
    "Go to 'Borrow Equipment' and select items you need": {"en": "Go to 'Borrow Equipment' and select items you need", "id": "Buka 'Pinjam Peralatan' dan pilih barang yang Anda butuhkan"},
    "Add to Cart": {"en": "Add to Cart", "id": "Tambah ke Keranjang"},
    "Choose quantity and due date for each item": {"en": "Choose quantity and due date for each item", "id": "Pilih jumlah dan tanggal jatuh tempo untuk setiap barang"},
    "Checkout": {"en": "Checkout", "id": "Selesaikan Peminjaman"},
    "Confirm your borrowing session and get a QR code": {"en": "Confirm your borrowing session and get a QR code", "id": "Konfirmasi sesi peminjaman dan dapatkan kode QR"},
    "Return": {"en": "Return", "id": "Kembalikan"},
    "Show the QR code to admin when returning items": {"en": "Show the QR code to admin when returning items", "id": "Tunjukkan kode QR ke admin saat mengembalikan barang"},
    "Select an option from the left menu to get started": {"en": "Select an option from the left menu to get started", "id": "Pilih opsi dari menu kiri untuk memulai"},
    # Borrow Equipment:
    "Welcome back": {"en": "Welcome back", "id": "Selamat datang kembali"},
    "Borrow Equipment": {"en": "Borrow Equipment", "id": "Pinjam Peralatan"},
    "My Loans": {"en": "My Loans", "id": "Pinjaman Saya"},
    "Profile": {"en": "Profile", "id": "Profil"},
    "Logout": {"en": "Logout", "id": "Keluar"},
    "Available Equipment": {"en": "Available Equipment", "id": "Peralatan Tersedia"},
    "Name": {"en": "Name", "id": "Nama"},
    "Amount": {"en": "Amount", "id": "Jumlah"},
    "Availability": {"en": "Availability", "id": "Ketersediaan"},
    "Action": {"en": "Action", "id": "Tindakan"},
    "Available": {"en": "Available", "id": "Tersedia"},
    "Out of stock": {"en": "Out of stock", "id": "Habis"},
    "Borrow": {"en": "Borrow", "id": "Pinjam"},
    "Next": {"en": "Next", "id": "Selanjutnya"},
    # Cart:
    "Your Cart": {"en": "Your Cart", "id": "Keranjang Anda"},
    "Item": {"en": "Item", "id": "Barang"},
    "Quantity": {"en": "Quantity", "id": "Jumlah"},
    "Due Date": {"en": "Due Date", "id": "Tanggal Jatuh Tempo"},
    "Confirm Borrowing": {"en": "Confirm Borrowing", "id": "Konfirmasi Peminjaman"},
    "Cart is empty": {"en": "Cart is empty", "id": "Keranjang kosong"},
    # Success loan:
    "Your Borrowing QR Code": {"en": "Your Borrowing QR Code", "id": "Kode QR Peminjaman Anda"},
    "Session": {"en": "Session", "id": "Sesi"},
    "Due date": {"en": "Due date", "id": "Tanggal jatuh tempo"},
    "Show this QR code to admin when returning items": {"en": "Show this QR code to admin when returning items", "id": "Tunjukkan kode QR ini ke admin saat mengembalikan barang"},
    "View My Loans": {"en": "View My Loans", "id": "Lihat Pinjaman Saya"},
    # My Loan:
    "Welcome back": {"en": "Welcome back", "id": "Selamat datang kembali"},
    "Borrow Equipment": {"en": "Borrow Equipment", "id": "Pinjam Peralatan"},
    "My Loans": {"en": "My Loans", "id": "Pinjaman Saya"},
    "Profile": {"en": "Profile", "id": "Profil"},
    "Logout": {"en": "Logout", "id": "Keluar"},
    "My Loans": {"en": "My Loans", "id": "Pinjaman Saya"},
    "Due Date": {"en": "Due Date", "id": "Tanggal Jatuh Tempo"},
    "Status": {"en": "Status", "id": "Status"},
    "Details": {"en": "Details", "id": "Detail"},
    "View Details": {"en": "View Details", "id": "Lihat Detail"},
    "Active": {"en": "Active", "id": "Aktif"},
    "LATE": {"en": "LATE", "id": "TERLAMBAT"},
    "Returned": {"en": "Returned", "id": "Dikembalikan"},
    "normal": {"en": "normal", "id": "normal"},
    "active": {"en": "active", "id": "aktif"},
    "damaged": {"en": "damaged", "id": "rusak"},
    "missing": {"en": "missing", "id": "hilang"},
    # View Detail:
    "Loan Details": {"en": "Loan Details", "id": "Detail Pinjaman"},
    "Borrow Date": {"en": "Borrow Date", "id": "Tanggal Pinjam"},
    "Due Date": {"en": "Due Date", "id": "Tanggal Jatuh Tempo"},
    "Status": {"en": "Status", "id": "Status"},
    "Active": {"en": "Active", "id": "Aktif"},
    "Items Borrowed": {"en": "Items Borrowed", "id": "Barang yang Dipinjam"},
    "Item": {"en": "Item", "id": "Barang"},
    "Quantity": {"en": "Quantity", "id": "Jumlah"},
    "Show QR Code": {"en": "Show QR Code", "id": "Tampilkan Kode QR"},
    "Back to My Loans": {"en": "Back to My Loans", "id": "Kembali ke Pinjaman Saya"},
    # Show QR:
    "Your Borrowing QR Code": {"en": "Your Borrowing QR Code", "id": "Kode QR Peminjaman Anda"},
    "Session": {"en": "Session", "id": "Sesi"},
    "Due date": {"en": "Due date", "id": "Tanggal jatuh tempo"},
    "Show this QR code to admin when returning items": {"en": "Show this QR code to admin when returning items", "id": "Tunjukkan kode QR ini ke admin saat mengembalikan barang"},
    "View My Loans": {"en": "View My Loans", "id": "Lihat Pinjaman Saya"},
    # Profile.html:
    "Welcome back": {"en": "Welcome back", "id": "Selamat datang kembali"},
    "Borrow Equipment": {"en": "Borrow Equipment", "id": "Pinjam Peralatan"},
    "My Loans": {"en": "My Loans", "id": "Pinjaman Saya"},
    "Profile": {"en": "Profile", "id": "Profil"},
    "Logout": {"en": "Logout", "id": "Keluar"},
    "Profile": {"en": "Profile", "id": "Profil"},
    "Username": {"en": "Username", "id": "Nama Pengguna"},
    "Full Name": {"en": "Full Name", "id": "Nama Lengkap"},
    "New Password": {"en": "New Password", "id": "Kata Sandi Baru"},
    "Leave blank to keep unchanged": {"en": "Leave blank to keep unchanged", "id": "Kosongkan jika tidak ingin mengubah"},
    "Update Profile": {"en": "Update Profile", "id": "Perbarui Profil"},
    "Profile updated successfully!": {"en": "Profile updated successfully!", "id": "Profil berhasil diperbarui!"},
    # Admin Dashboard:
    "Admin Panel": {"en": "Admin Panel", "id": "Panel Admin"},
    "Dashboard": {"en": "Dashboard", "id": "Dasbor"},
    "Scan QR": {"en": "Scan QR", "id": "Pindai QR"},
    "Logout": {"en": "Logout", "id": "Keluar"},
    "Equipment Management": {"en": "Equipment Management", "id": "Manajemen Peralatan"},
    "Name": {"en": "Name", "id": "Nama"},
    "Amount": {"en": "Amount", "id": "Jumlah"},
    "Add New Equipment": {"en": "Add New Equipment", "id": "Tambah Peralatan Baru"},
    "Equipment Name": {"en": "Equipment Name", "id": "Nama Peralatan"},
    "Initial Amount": {"en": "Initial Amount", "id": "Jumlah Semula"},
    "Add Equipment": {"en": "Add Equipment", "id": "Tambah Peralatan"},
    "Update Equipment": {"en": "Update Equipment", "id": "Update Peralatan"},
    "Equipment ID": {"en": "Equipment ID", "id": "ID Peralatan"},
    "New Name (optional)": {"en": "New Name (optional)", "id": "Nama Baru (opsional)"},
    "New Amount (optional)": {"en": "New Amount (optional)", "id": "Jumlah Baru (opsional)"},
    "Update": {"en": "Update", "id": "Perbarui"},
    "Delete Equipment": {"en": "Delete Equipment", "id": "Hapus Peralatan"},
    "Delete": {"en": "Delete", "id": "Hapus"},
    "Borrowing Sessions": {"en": "Borrowing Sessions", "id": "Sesi Peminjaman"},
    "User": {"en": "User", "id": "Pengguna"},
    "Borrow Date": {"en": "Borrow Date", "id": "Tanggal Pinjam"},
    "Due Date": {"en": "Due Date", "id": "Tanggal Jatuh Tempo"},
    "Return Date": {"en": "Return Date", "id": "Tanggal Kembali"},
    "Status": {"en": "Status", "id": "Status"},
    "Active": {"en": "Active", "id": "Aktif"},
    "Items": {"en": "Items", "id": "Barang"},
    # Scan_QR.html:
    "Scan QR Code": {"en": "Scan QR Code", "id": "Pindai Kode QR"},
    "Upload an image containing the QR code, or use your camera.": {"en": "Upload an image containing the QR code, or use your camera.", "id": "Unggah gambar yang berisi kode QR, atau gunakan kamera."},
    "Start Camera": {"en": "Start Camera", "id": "Nyalakan Kamera"},
    "Stop Camera": {"en": "Stop Camera", "id": "Matikan Kamera"},
    "Invalid QR code (no valid return URL).": {"en": "Invalid QR code (no valid return URL).", "id": "Kode QR tidak valid (bukan URL pengembalian)."},
    "No QR code found in image.": {"en": "No QR code found in image.", "id": "Tidak ada kode QR dalam gambar."},
    "Camera access denied or not available.": {"en": "Camera access denied or not available.", "id": "Akses kamera ditolak atau tidak tersedia."},
    "Invalid QR code (not a return URL).": {"en": "Invalid QR code (not a return URL).", "id": "Kode QR tidak valid (bukan URL pengembalian)."},
    "Admin": {"en": "Admin", "id": "Admin"},
    "Dashboard": {"en": "Dashboard", "id": "Dasbor"},
    "Scan QR": {"en": "Scan QR", "id": "Pindai QR"},
    "Logout": {"en": "Logout", "id": "Keluar"},
    # return_session.html:
    "Return Borrowing Session": {"en": "Return Borrowing Session", "id": "Kembalikan Sesi Peminjaman"},
    "User:": {"en": "User:", "id": "Pengguna:"},
    "Borrow Date:": {"en": "Borrow Date:", "id": "Tanggal Pinjam:"},
    "Due Date:": {"en": "Due Date:", "id": "Tanggal Jatuh Tempo:"},
    "Items:": {"en": "Items:", "id": "Barang:"},
    "Equipment": {"en": "Equipment", "id": "Peralatan"},
    "Quantity": {"en": "Quantity", "id": "Jumlah"},
    "Return status:": {"en": "Return status:", "id": "Status pengembalian:"},
    "Normal (return items to stock)": {"en": "Normal (return items to stock)", "id": "Normal (kembalikan barang ke stok)"},
    "Missing (items not returned)": {"en": "Missing (items not returned)", "id": "Hilang (barang tidak dikembalikan)"},
    "Damaged": {"en": "Damaged", "id": "Rusak"},
    "Note (optional):": {"en": "Note (optional):", "id": "Catatan (opsional):"},
    "Process Return": {"en": "Process Return", "id": "Proses Pengembalian"},
}

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='admin123', name='Administrator', role='admin')
        db.session.add(admin)
        db.session.commit()

def generate_token():
    return secrets.token_urlsafe(16)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        role = request.form['role']
        if User.query.filter_by(username=username).first():
            return "Username already exists", 400
        user = User(username=username, password=password, name=name, role=role)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('customer_dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if not user:
            return "Invalid credentials", 401
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('customer_dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/customer/dashboard')
def customer_dashboard():
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    return render_template('customer_dashboard.html')

@app.route('/customer/borrow')
def borrow_equipment():
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    equipment = Equipment.query.all()
    return render_template('borrow_equipment.html', equipment=equipment)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    data = request.get_json()
    cart = data.get('cart', [])
    session['temp_cart'] = cart
    return jsonify({'success': True})

@app.route('/cart')
def view_cart():
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    cart = session.get('temp_cart', [])
    items = []
    for item in cart:
        equip = Equipment.query.get(item['equipment_id'])
        if equip:
            items.append({
                'equipment': equip,
                'quantity': item['quantity']
            })
    now = datetime.now()
    default_due = (now + timedelta(days=7)).strftime('%Y-%m-%d')
    return render_template('cart.html', items=items, now=now, default_due=default_due)

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    due_date_str = request.form['due_date']
    due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
    if due_date < datetime.now():
        return "Due date cannot be in the past", 400
    cart = session.pop('temp_cart', [])
    if not cart:
        return "Cart empty", 400
    user = User.query.get(session['user_id'])
    token = generate_token()
    borrow_session = BorrowSession(
        user_id=user.id,
        due_date=due_date,
        qr_token=token
    )
    db.session.add(borrow_session)
    db.session.flush()
    for item in cart:
        equip = Equipment.query.get(item['equipment_id'])
        if equip.amount < item['quantity']:
            db.session.rollback()
            return f"Not enough {equip.name} available", 400
        borrow_item = BorrowItem(
            session_id=borrow_session.id,
            equipment_id=equip.id,
            quantity=item['quantity']
        )
        equip.amount -= item['quantity']
        db.session.add(borrow_item)
    db.session.commit()
    qr_url = url_for('admin_return_session', token=token, _external=True)
    qr_base64 = generate_qr_code_base64(qr_url)
    return render_template('checkout_success.html', borrow_session=borrow_session, qr_base64=qr_base64)

@app.route('/customer/my_loans')
def my_loans():
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    sessions = BorrowSession.query.filter_by(user_id=user.id).order_by(BorrowSession.borrow_date.desc()).all()
    for sess in sessions:
        sess.is_late = (datetime.now() > sess.due_date and sess.return_date is None)
    return render_template('my_loans.html', sessions=sessions)

@app.route('/customer/loan_details/<int:session_id>')
def loan_details(session_id):
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    sess = BorrowSession.query.get_or_404(session_id)
    if sess.user_id != session['user_id']:
        return "Unauthorized", 401
    items = sess.items
    sess.is_late = (datetime.now() > sess.due_date and sess.return_date is None)
    return render_template('loan_details.html', borrow_session=sess, items=items)

@app.route('/customer/show_qr/<int:session_id>')
def show_session_qr(session_id):
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    sess = BorrowSession.query.get_or_404(session_id)
    if sess.user_id != session['user_id']:
        return "Unauthorized", 401
    qr_url = url_for('admin_return_session', token=sess.qr_token, _external=True)
    qr_base64 = generate_qr_code_base64(qr_url)
    return render_template('qr_modal.html', borrow_session=sess, qr_base64=qr_base64)

@app.route('/customer/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        new_username = request.form['username']
        new_name = request.form['name']
        new_password = request.form['password']
        if new_username:
            user.username = new_username
        if new_name:
            user.name = new_name
        if new_password:
            user.password = new_password
        db.session.commit()
        session['username'] = user.username
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', user=user)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password, role='admin').first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid admin credentials", 401
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    equipment = Equipment.query.all()
    sessions = BorrowSession.query.order_by(BorrowSession.borrow_date.desc()).all()
    return render_template('admin_dashboard.html', equipment=equipment, sessions=sessions)

@app.route('/admin/edit_equipment', methods=['POST'])
def admin_edit_equipment():
    if session.get('role') != 'admin':
        return "Unauthorized", 401
    action = request.form['action']

    if action == 'add':
        name = request.form.get('name', '').strip()
        amount_str = request.form.get('amount', '')
        if not name or not amount_str:
            return "Name and amount are required", 400
        amount = int(amount_str)
        equip = Equipment(name=name, amount=amount)
        db.session.add(equip)

    elif action == 'update':
        equip_id = request.form.get('id')
        if not equip_id:
            return "Equipment ID required", 400
        equip = Equipment.query.get(equip_id)
        if not equip:
            return "Equipment not found", 404

        new_name = request.form.get('name', '').strip()
        new_amount_str = request.form.get('amount', '').strip()

        if new_name:
            equip.name = new_name
        if new_amount_str:
            equip.amount = int(new_amount_str)

    elif action == 'delete':
        equip_id = request.form.get('id')
        if not equip_id:
            return "Equipment ID required", 400
        equip = Equipment.query.get(equip_id)
        if equip:
            active_loan = BorrowItem.query.filter_by(equipment_id=equip.id).join(BorrowSession).filter(BorrowSession.return_date.is_(None)).first()
            if active_loan:
                return "Cannot delete: equipment is currently borrowed", 400
            db.session.delete(equip)
        else:
            return "Equipment not found", 404

    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/return/<token>')
def admin_return_session(token):
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    sess = BorrowSession.query.filter_by(qr_token=token).first()
    if not sess:
        return "Invalid QR", 404
    if sess.return_date:
        return "Already returned", 400
    items = sess.items
    return render_template('return_session.html', session=sess, items=items)

@app.route('/admin/process_return', methods=['POST'])
def admin_process_return():
    if session.get('role') != 'admin':
        return "Unauthorized", 401
    session_id = request.form['session_id']
    action = request.form['action']
    note = request.form.get('note', '')
    sess = BorrowSession.query.get_or_404(session_id)
    if sess.return_date:
        return "Already returned", 400
    sess.return_date = datetime.now()
    sess.return_status = action
    sess.return_note = note
    if action == 'normal':
        for item in sess.items:
            equip = Equipment.query.get(item.equipment_id)
            equip.amount += item.quantity
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/scan_qr')
def admin_scan_qr():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    return render_template('admin_scan_qr.html')

@app.route('/admin/profile', methods=['GET', 'POST'])
def admin_profile():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        new_username = request.form['username']
        new_name = request.form['name']
        new_password = request.form['password']
        if new_username:
            user.username = new_username
        if new_name:
            user.name = new_name
        if new_password:
            user.password = new_password
        db.session.commit()
        session['username'] = user.username
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('admin_profile'))
    return render_template('admin_profile.html', user=user)

@app.route('/toggle_language')
def toggle_language():
    current = session.get('lang', 'en')
    session['lang'] = 'id' if current == 'en' else 'en'
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    else:
        return redirect(url_for('index'))

@app.context_processor
def inject_utils():
    lang = session.get('lang', 'en')
    def _(text):
        return translations.get(text, {}).get(lang, text)
    return {'lang': lang, '_': _}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
