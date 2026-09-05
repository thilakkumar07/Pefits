from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
app = Flask(__name__)

# Helper function for database configuration
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="thilak123",
        database="finance_db"
    )

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) # returns rows as dictionaries

    # 1. Fetch all expenses ordered by latest
    cursor.execute("SELECT * FROM expenses ORDER BY date_added DESC")
    expenses = cursor.fetchall()

    # 2. Fetch total sum of expenses
    cursor.execute("SELECT SUM(amount) AS total FROM expenses")
    total_result = cursor.fetchone()
    total_spent = total_result['total'] if total_result['total'] else 0.00

    cursor.close()
    conn.close()

    return render_template('index.html', expenses=expenses, total_spent=total_spent)

@app.route('/add', methods=['POST'])
def add_expenses():

    # Grab data out of the HTML form inputs
    title = request.form['title']
    amount = request.form['amount']
    category = request.form['category']
    
    # Grab the manual date from the UI picker
    chosen_date = request.form['expense_date']

    # If the user leaves the box empty, default it to today's date
    if not chosen_date:
        chosen_date = date.today().strftime('%Y-%m-%d')

    # Insert it directly into MYSQL
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (title, amount, category, expense_date) VALUES (%s, %s, %s, %s)",
        (title, amount, category, chosen_date)
    )
    conn.commit() # For saving changes
    cursor.close()
    conn.close()

    return redirect(url_for('index'))


@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    # Connect to database
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id = %s", (expense_id, )
    )
    conn.commit()

    cursor.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/clear_all', methods=['POST'])
def clear_all_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("TRUNCATE TABLE expenses")
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)


