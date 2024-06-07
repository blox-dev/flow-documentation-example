from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

current_file_location = os.path.dirname(__file__)

DATABASE = os.path.join(current_file_location, 'payments.db')

def create_payments_table(reset=False):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if reset:
        cursor.execute('''DROP TABLE IF EXISTS payments''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS payments
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       order_id INTEGER NOT NULL,
                       user_id INTEGER NOT NULL,
                       payment_method TEXT NOT NULL,
                       amount REAL NOT NULL,
                       transaction_date TEXT NOT NULL,
                       status TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def populate_payments_table():
    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # List of hardcoded payment data
    payment_data = [
    # id,order_id, user_id, payment_method,amount,  transaction_date,      status
        (1,        1,       'credit card', 1199.98, '2024-04-23 09:00:00', 'completed'),
        (2, 2, 'paypal', 19.99, '2024-04-23 09:15:00', 'completed'),
        (3, 3, 'credit card', 119.97, '2024-04-23 09:30:00', 'completed'),
        (4, 4, 'cash on delivery', 89.99, '2024-04-23 09:45:00', 'completed'),
        (5, 5, 'credit card', 59.98, '2024-04-23 10:00:00', 'completed'),
        (6, 1, 'paypal', 14.99, '2024-04-23 10:15:00', 'completed'),
        (7, 2, 'credit card', 199.96, '2024-04-23 10:30:00', 'completed'),
        (8, 3, 'paypal', 4.99, '2024-04-23 10:45:00', 'completed'),
        (9, 4, 'credit card', 49.98, '2024-04-23 11:00:00', 'completed'),
        (10, 5, 'paypal', 999.99, '2024-04-23 11:15:00', 'completed'),
        (11, 1, 'credit card', 179.97, '2024-04-23 11:30:00', 'completed'),
        (12, 2, 'paypal', 9.99, '2024-04-23 11:45:00', 'completed'),
        (13, 3, 'credit card', 79.98, '2024-04-23 12:00:00', 'completed'),
        (14, 4, 'cash on delivery', 2.99, '2024-04-23 12:15:00', 'completed'),
        (15, 5, 'credit card', 69.98, '2024-04-23 12:30:00', 'completed'),
        (16, 1, 'paypal', 199.99, '2024-04-23 12:45:00', 'completed'),
        (17, 2, 'credit card', 149.97, '2024-04-23 13:00:00', 'completed'),
        (18, 3, 'cash on delivery', 69.99, '2024-04-23 13:15:00', 'completed'),
        (19, 4, 'credit card', 1999.98, '2024-04-23 13:30:00', 'completed'),
        (20, 5, 'paypal', 49.99, '2024-04-23 13:45:00', 'completed'),
    ]

    # Insert hardcoded payment data into the database
    for payment in payment_data:
        cursor.execute('''INSERT INTO payments (order_id, user_id, payment_method, amount, transaction_date, status)
                        VALUES (?, ?, ?, ?, ?, ?)''', payment)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

create_payments_table(reset=True)
populate_payments_table()

@app.route('/payments/update_status/<int:payment_id>', methods=['PUT'])
def update_payment_status(payment_id):
    data = request.json
    status = data.get('status')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute('''UPDATE payments SET status=? WHERE id=?''', (status, payment_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Payment status updated successfully'}), 200
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/payments/order/<int:order_id>', methods=['GET'])
def get_payments_by_order_id(order_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM payments WHERE order_id=?''', (order_id,))
    payments = cursor.fetchall()
    conn.close()

    payment_list = []
    for payment in payments:
        payment_data = {
            'id': payment[0],
            'order_id': payment[1],
            'user_id': payment[2],
            'payment_method': payment[3],
            'amount': payment[4],
            'transaction_date': payment[5],
            'status': payment[6]
        }
        payment_list.append(payment_data)

    return jsonify(payment_list), 200

@app.route('/payments/user/<int:user_id>', methods=['GET'])
def get_payments_by_user_id(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM payments WHERE user_id=?''', (user_id,))
    payments = cursor.fetchall()
    conn.close()

    payment_list = []
    for payment in payments:
        payment_data = {
            'id': payment[0],
            'order_id': payment[1],
            'user_id': payment[2],
            'payment_method': payment[3],
            'amount': payment[4],
            'transaction_date': payment[5],
            'status': payment[6]
        }
        payment_list.append(payment_data)

    return jsonify(payment_list), 200

@app.route('/payments/process', methods=['POST'])
def process_payment():
    data = request.json
    order_id = data.get('order_id')
    user_id = data.get('user_id')
    payment_method = data.get('payment_method')
    amount = data.get('amount')
    transaction_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Use current time as payment date
    status = 'pending'  # Default status for newly initiated payments

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute('''INSERT INTO payments (order_id, user_id, payment_method, amount, transaction_date, status)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (order_id, user_id, payment_method, amount, transaction_date, status))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Payment processed successfully'}), 201
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': str(e)}), 400


@app.route('/payments/status/<string:status>', methods=['GET'])
def get_payments_by_status(status):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM payments WHERE status=?''', (status,))
    payments = cursor.fetchall()
    conn.close()

    payment_list = []
    for payment in payments:
        payment_data = {
            'id': payment[0],
            'order_id': payment[1],
            'user_id': payment[2],
            'payment_method': payment[3],
            'amount': payment[4],
            'transaction_date': payment[5],
            'status': payment[6]
        }
        payment_list.append(payment_data)

    return jsonify(payment_list), 200

@app.route('/payments/total_revenue', methods=['GET'])
def calculate_total_revenue():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT SUM(amount) FROM payments WHERE status='paid' ''')
    total_revenue = cursor.fetchone()[0]
    conn.close()

    return jsonify({'total_revenue': total_revenue}), 200

if __name__ == '__main__':
    app.run(host='localhost', port=9054, debug=True)