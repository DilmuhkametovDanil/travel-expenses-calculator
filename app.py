from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT
        )
    ''')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM budget')
    if cursor.fetchone() is None:
        conn.execute('INSERT INTO budget (amount) VALUES (50000)')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    budget_row = conn.execute('SELECT amount FROM budget LIMIT 1').fetchone()
    total_budget = budget_row['amount'] if budget_row else 50000
    
    selected_category = request.args.get('category', '')
    if selected_category:
        expenses = conn.execute('SELECT * FROM expenses WHERE category = ?', (selected_category,)).fetchall()
    else:
        expenses = conn.execute('SELECT * FROM expenses').fetchall()
        
    total_spent = sum(item['amount'] for item in expenses)
    if selected_category:
        all_expenses = conn.execute('SELECT * FROM expenses').fetchall()
        total_spent = sum(item['amount'] for item in all_expenses)

    remaining_budget = total_budget - total_spent
    
    if total_budget > 0:
        progress_percent = min((total_spent / total_budget) * 100, 100)
    else:
        progress_percent = 0
        
    conn.close()
    return render_template(
        'index.html', 
        expenses=expenses, 
        total_budget=total_budget, 
        total_spent=total_spent, 
        remaining_budget=remaining_budget,
        progress_percent=progress_percent,
        selected_category=selected_category
    )

@app.route('/add', methods=['POST'])
def add_expense():
    category = request.form['category']
    amount = request.form['amount']
    description = request.form['description']
    if amount:
        conn = get_db_connection()
        conn.execute('INSERT INTO expenses (category, amount, description) VALUES (?, ?, ?)',
                     (category, float(amount), description))
        conn.commit()
        conn.close()
    return redirect('/')

@app.route('/update_budget', methods=['POST'])
def update_budget():
    new_budget = request.form['new_budget']
    if new_budget:
        conn = get_db_connection()
        conn.execute('UPDATE budget SET amount = ? WHERE id = 1', (float(new_budget),))
        conn.commit()
        conn.close()
    return redirect('/')

@app.route('/delete/<int:id>')
def delete_expense(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM expenses WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
