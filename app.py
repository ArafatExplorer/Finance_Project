from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key

# Hardcoded user credentials with PIN (for simplicity)
users = {
    "admin": {"password": "12345", "pin": "1234"},
    "user2": {"password": "password2", "pin": "5678"}
}

# Predefined categories
categories = [
    "Salary", "Freelance", "Investment", "Gift", "Other Income",  # Income categories
    "Food", "Transport", "Rent", "Utilities", "Entertainment", "Shopping", "Other Expense"  # Expense categories
]

# In-memory storage for transactions (for simplicity)
transactions = []

# Routes
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    balance = sum(t['amount'] for t in transactions if t['type'] == 'income') - \
              sum(t['amount'] for t in transactions if t['type'] == 'expense')
    return render_template('index.html', transactions=transactions, balance=balance)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username]['password'] == password:
            session['username'] = username  # Store username in session
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        type = request.form['type']
        category = request.form['category']
        amount = float(request.form['amount'])
        description = request.form['description']
        date = request.form['date']  # Get the date from the form

        transaction = {
            'type': type,
            'category': category,
            'amount': amount,
            'description': description,
            'date': date  # Add date to the transaction
        }
        transactions.append(transaction)
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add_transaction.html', categories=categories)

@app.route('/delete/<int:index>', methods=['GET', 'POST'])
def delete_transaction(index):
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        pin = request.form['pin']
        if pin == users[session['username']]['pin']:
            if 0 <= index < len(transactions):
                deleted_transaction = transactions.pop(index)
                flash(f"Deleted transaction: {deleted_transaction['description']}", 'success')
            else:
                flash('Invalid transaction index.', 'danger')
        else:
            flash('Incorrect PIN. Deletion failed.', 'danger')

        return redirect(url_for('index'))

    return render_template('confirm_delete.html', index=index)

@app.route('/print', methods=['GET', 'POST'])
def print_transactions():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        # Filter transactions by date range
        filtered_transactions = [t for t in transactions if start_date <= t['date'] <= end_date]
        balance = sum(t['amount'] for t in filtered_transactions if t['type'] == 'income') - \
                  sum(t['amount'] for t in filtered_transactions if t['type'] == 'expense')

        return render_template('print.html', transactions=filtered_transactions, balance=balance,
                               start_date=start_date, end_date=end_date)

    return render_template('print.html', transactions=[], balance=0, start_date='', end_date='')

if __name__ == '__main__':
    app.run(debug=True)