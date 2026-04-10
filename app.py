from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

init_db()  

# Database initialization
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('buyer', 'vendor'))
    )''')
    
    # Tenders table
    c.execute('''CREATE TABLE IF NOT EXISTS tenders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        deadline TEXT NOT NULL,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users (id)
    )''')
    
    # Bids table
    c.execute('''CREATE TABLE IF NOT EXISTS bids (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tender_id INTEGER,
        vendor_id INTEGER,
        bid_amount REAL NOT NULL,
        proposal_text TEXT NOT NULL,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tender_id) REFERENCES tenders (id),
        FOREIGN KEY (vendor_id) REFERENCES users (id)
    )''')
    
    # Insert sample data
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        sample_users = [
            ('Sample Buyer', 'buyer1@example.com', generate_password_hash('buyer123'), 'buyer'),
            ('Sample Vendor', 'vendor1@example.com', generate_password_hash('vendor123'), 'vendor')
        ]
        c.executemany("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)", sample_users)
    
    conn.commit()
    conn.close()

# Database helper functions
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'database.db')

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Login required decorator
def login_required(role=None):
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first!', 'error')
                return redirect(url_for('login'))
            
            if role and session.get('role') != role:
                flash('Access denied! Wrong user role.', 'error')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        if not all([name, email, password]):
            flash('Please fill all fields!', 'error')
            return render_template('register.html')
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if email exists
        c.execute("SELECT id FROM users WHERE email = ?", (email,))
        if c.fetchone():
            flash('Email already registered!', 'error')
            conn.close()
            return render_template('register.html')
        
        # Insert user
        hashed_password = generate_password_hash(password)
        c.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                 (name, email, hashed_password, role))
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['role'] = user['role']
            flash(f'Welcome back, {user["name"]}!', 'success')
            if user['role'] == 'buyer':
                return redirect(url_for('buyer_dashboard'))
            else:
                return redirect(url_for('vendor_dashboard'))
        else:
            flash('Invalid email or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

# Buyer Routes
@app.route('/buyer_dashboard')
@login_required('buyer')
def buyer_dashboard():
    conn = get_db_connection()
    tenders = conn.execute("SELECT * FROM tenders WHERE created_by = ? ORDER BY created_at DESC", 
                          (session['user_id'],)).fetchall()
    conn.close()
    return render_template('buyer_dashboard.html', tenders=tenders)

@app.route('/create_tender', methods=['GET', 'POST'])
@login_required('buyer')
def create_tender():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']
        
        if not all([title, description, deadline]):
            flash('Please fill all fields!', 'error')
            return render_template('create_tender.html')
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO tenders (title, description, deadline, created_by) VALUES (?, ?, ?, ?)",
                 (title, description, deadline, session['user_id']))
        conn.commit()
        conn.close()
        
        flash('Tender created successfully!', 'success')
        return redirect(url_for('buyer_dashboard'))
    
    return render_template('create_tender.html')

@app.route('/view_bids/<int:tender_id>')
@login_required('buyer')
def view_bids(tender_id):
    conn = get_db_connection()
    
    # Get tender details
    tender = conn.execute("SELECT * FROM tenders WHERE id = ? AND created_by = ?", 
                         (tender_id, session['user_id'])).fetchone()
    
    if not tender:
        flash('Tender not found or access denied!', 'error')
        conn.close()
        return redirect(url_for('buyer_dashboard'))
    
    # Get bids for this tender
    bids = conn.execute("""
        SELECT b.*, u.name as vendor_name 
        FROM bids b 
        JOIN users u ON b.vendor_id = u.id 
        WHERE b.tender_id = ? 
        ORDER BY b.bid_amount ASC, b.submitted_at DESC
    """, (tender_id,)).fetchall()
    
    conn.close()
    return render_template('view_bids.html', tender=tender, bids=bids)

# Vendor Routes
@app.route('/vendor_dashboard')
@login_required('vendor')
def vendor_dashboard():
    conn = get_db_connection()
    tenders = conn.execute("""
        SELECT t.*, u.name as buyer_name 
        FROM tenders t 
        JOIN users u ON t.created_by = u.id 
        ORDER BY t.created_at DESC
    """).fetchall()
    conn.close()
    return render_template('vendor_dashboard.html', tenders=tenders)

@app.route('/submit_bid/<int:tender_id>', methods=['GET', 'POST'])
@login_required('vendor')
def submit_bid(tender_id):
    conn = get_db_connection()
    
    # Check if tender exists
    tender = conn.execute("SELECT * FROM tenders WHERE id = ?", (tender_id,)).fetchone()
    if not tender:
        flash('Tender not found!', 'error')
        conn.close()
        return redirect(url_for('vendor_dashboard'))
    
    if request.method == 'POST':
        bid_amount = float(request.form['bid_amount'])
        proposal_text = request.form['proposal_text']
        
        if bid_amount <= 0 or not proposal_text.strip():
            flash('Invalid bid amount or proposal!', 'error')
            conn.close()
            return render_template('submit_bid.html', tender=tender)
        
        c = conn.cursor()
        c.execute("""
            INSERT INTO bids (tender_id, vendor_id, bid_amount, proposal_text) 
            VALUES (?, ?, ?, ?)
        """, (tender_id, session['user_id'], bid_amount, proposal_text))
        conn.commit()
        conn.close()
        
        flash('Bid submitted successfully!', 'success')
        return redirect(url_for('vendor_dashboard'))
    
    conn.close()
    return render_template('submit_bid.html', tender=tender)

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)