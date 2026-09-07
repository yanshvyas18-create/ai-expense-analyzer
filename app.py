from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import joblib
import os
import datetime

app = Flask(__name__)

DB_NAME = 'expenses.db'

# --- DATABASE SETUP ---
def get_db_connection():
    # Connects to SQLite database and allows us to access rows like dictionaries
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Create the expenses table if it does not exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # If the database is completely empty, insert some sample data to make the dashboard look good
    count = conn.execute('SELECT COUNT(*) FROM expenses').fetchone()[0]
    if count == 0:
        print("Inserting sample data into the database...")
        sample_data = [
            ('Zomato dinner', 450, 'Food', '2026-09-01'),
            ('Uber ride', 150, 'Travel', '2026-09-02'),
            ('Electricity bill', 1200, 'Bills', '2026-09-03'),
            ('Amazon shoes', 1500, 'Shopping', '2026-09-05'),
            ('Swiggy lunch', 300, 'Food', '2026-09-06'),
            ('Netflix subscription', 199, 'Entertainment', '2026-09-06')
        ]
        conn.executemany('INSERT INTO expenses (description, amount, category, date) VALUES (?, ?, ?, ?)', sample_data)
        conn.commit()
    conn.close()

# Initialize DB when the app starts
init_db()

# --- LOAD MACHINE LEARNING MODEL ---
def load_ml_model():
    try:
        vectorizer = joblib.load('model/vectorizer.pkl')
        classifier = joblib.load('model/classifier.pkl')
        return vectorizer, classifier
    except FileNotFoundError:
        print("Warning: ML model not found. Please run 'python train_model.py' first.")
        return None, None

vectorizer, classifier = load_ml_model()


# --- ROUTES ---

@app.route('/')
def dashboard():
    conn = get_db_connection()
    
    # Get basic statistics
    total_expenses = conn.execute('SELECT SUM(amount) FROM expenses').fetchone()[0] or 0
    tx_count = conn.execute('SELECT COUNT(*) FROM expenses').fetchone()[0]
    avg_expense = conn.execute('SELECT AVG(amount) FROM expenses').fetchone()[0] or 0
    
    highest_cat_row = conn.execute('SELECT category FROM expenses GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1').fetchone()
    highest_category = highest_cat_row[0] if highest_cat_row else "None"
    
    # Get category data for the pie chart
    category_data = conn.execute('SELECT category, SUM(amount) as total FROM expenses GROUP BY category').fetchall()
    cat_labels = [row['category'] for row in category_data]
    cat_amounts = [row['total'] for row in category_data]

    # Get monthly spending data for bar chart
    monthly_data = conn.execute("SELECT strftime('%Y-%m', date) as month, SUM(amount) as total FROM expenses GROUP BY month ORDER BY month").fetchall()
    month_labels = [row['month'] for row in monthly_data]
    month_amounts = [row['total'] for row in monthly_data]
    
    # Get recent transactions
    recent_tx = conn.execute('SELECT * FROM expenses ORDER BY date DESC, id DESC LIMIT 5').fetchall()
    
    conn.close()
    
    # Dynamic simple AI Insight for dashboard
    insight = "Add some expenses to see insights!"
    if highest_category != "None":
        insight = f"🤖 AI Insight: {highest_category} is your highest spending category."
    
    return render_template('dashboard.html', 
        total=round(total_expenses, 2), 
        count=tx_count, 
        avg=round(avg_expense, 2), 
        highest_cat=highest_category,
        cat_labels=cat_labels,
        cat_amounts=cat_amounts,
        month_labels=month_labels,
        month_amounts=month_amounts,
        recent_tx=recent_tx,
        insight=insight
    )


@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        description = request.form.get('description')
        amount = request.form.get('amount')
        date = request.form.get('date')
        category = request.form.get('category')
        
        # Simple validation
        if not description or not amount or not date or not category:
            return "Error: All fields are required!", 400
            
        try:
            amount = float(amount)
            if amount < 0:
                return "Error: Amount cannot be negative!", 400
        except ValueError:
            return "Error: Invalid amount!", 400
            
        conn = get_db_connection()
        conn.execute('INSERT INTO expenses (description, amount, category, date) VALUES (?, ?, ?, ?)',
                     (description, amount, category, date))
        conn.commit()
        conn.close()
        
        return redirect(url_for('transactions'))
        
    return render_template('add_expense.html')


@app.route('/api/predict', methods=['POST'])
def predict_category():
    # This endpoint is called via JavaScript from the Add Expense page
    data = request.get_json()
    description = data.get('description', '')
    
    if not description:
        return jsonify({'error': 'Description is empty'}), 400
        
    global vectorizer, classifier
    if vectorizer is None or classifier is None:
        vectorizer, classifier = load_ml_model() # Try loading again
        if vectorizer is None:
            return jsonify({'error': 'ML Model not trained.'}), 500
            
    # 1. Transform the text input into numbers
    features = vectorizer.transform([description])
    
    # 2. Predict the category using the trained classifier
    prediction = classifier.predict(features)[0]
    
    # Get confidence (probability)
    probs = classifier.predict_proba(features)[0]
    confidence = max(probs) * 100
    
    return jsonify({
        'category': prediction,
        'confidence': round(confidence, 2)
    })


@app.route('/transactions')
def transactions():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    conn = get_db_connection()
    
    query = 'SELECT * FROM expenses WHERE 1=1'
    params = []
    
    if search:
        query += ' AND description LIKE ?'
        params.append(f'%{search}%')
    if category:
        query += ' AND category = ?'
        params.append(category)
        
    query += ' ORDER BY date DESC, id DESC'
    
    transactions = conn.execute(query, params).fetchall()
    categories = conn.execute('SELECT DISTINCT category FROM expenses').fetchall()
    
    conn.close()
    return render_template('transactions.html', transactions=transactions, categories=categories, search=search, selected_category=category)


@app.route('/delete/<int:id>', methods=['POST'])
def delete_expense(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM expenses WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('transactions'))


@app.route('/analytics')
def analytics():
    conn = get_db_connection()
    
    category_data = conn.execute('SELECT category, SUM(amount) as total FROM expenses GROUP BY category').fetchall()
    cat_labels = [row['category'] for row in category_data]
    cat_amounts = [row['total'] for row in category_data]
    
    monthly_data = conn.execute("SELECT strftime('%Y-%m', date) as month, SUM(amount) as total FROM expenses GROUP BY month ORDER BY month").fetchall()
    month_labels = [row['month'] for row in monthly_data]
    month_amounts = [row['total'] for row in monthly_data]
    
    conn.close()
    
    return render_template('analytics.html', 
        cat_labels=cat_labels, 
        cat_amounts=cat_amounts,
        month_labels=month_labels,
        month_amounts=month_amounts
    )


@app.route('/insights')
def insights():
    # Simple Python logic to generate insights
    conn = get_db_connection()
    
    total = conn.execute('SELECT SUM(amount) FROM expenses').fetchone()[0] or 0
    count = conn.execute('SELECT COUNT(*) FROM expenses').fetchone()[0]
    
    if total == 0:
        return render_template('insights.html', insights=["No data available yet. Please add some expenses!"])
        
    category_data = conn.execute('SELECT category, SUM(amount) as total FROM expenses GROUP BY category ORDER BY total DESC').fetchall()
    
    insights_list = []
    
    # Insight 1: Top category
    top_cat = category_data[0]['category']
    top_cat_amt = category_data[0]['total']
    pct = round((top_cat_amt / total) * 100, 1)
    insights_list.append(f"🎯 Your highest spending category is {top_cat}, taking up {pct}% of your total budget (₹{top_cat_amt}).")
    
    # Insight 2: Transaction frequency
    insights_list.append(f"💳 You have made {count} transactions in total. Your average transaction size is ₹{round(total/count, 2)}.")
    
    # Insight 3: Lowest category
    if len(category_data) > 1:
        low_cat = category_data[-1]['category']
        insights_list.append(f"📉 You spend the least on {low_cat} (₹{category_data[-1]['total']}).")
        
    # Insight 4: Description checks
    food_count = conn.execute("SELECT COUNT(*) FROM expenses WHERE description LIKE '%zomato%' OR description LIKE '%swiggy%' COLLATE NOCASE").fetchone()[0]
    if food_count > 0:
        insights_list.append(f"🍔 You have ordered food delivery {food_count} times. Consider cooking at home to save money!")
        
    conn.close()
    
    return render_template('insights.html', insights=insights_list)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
