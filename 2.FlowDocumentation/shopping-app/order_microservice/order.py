from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

current_file_location = os.path.dirname(__file__)

DATABASE = os.path.join(current_file_location, 'orders.db')

def create_orders_table(reset=False):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if reset:
        cursor.execute('''DROP TABLE IF EXISTS orders''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS orders
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_id INTEGER NOT NULL,
                       order_date TEXT NOT NULL,
                       status TEXT NOT NULL,
                       total_price REAL NOT NULL,
                       payment_method TEXT,
                       payment_status TEXT)''')
    conn.commit()
    conn.close()

def populate_orders_table():
    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # List of hardcoded order data
    order_data = [
    # id, user_id, order_date,            status,   total_price, payment_method, payment_status
        ( 1,       '2024-04-23 09:00:00', 'pending', 1199.98,    'credit card', 'pending'),
        (2, '2024-04-23 09:15:00', 'shipped', 19.99, 'paypal', 'paid'),
        (3, '2024-04-23 09:30:00', 'pending', 119.97, 'credit card', 'pending'),
        (4, '2024-04-23 09:45:00', 'delivered', 89.99, 'cash on delivery', 'paid'),
        (5, '2024-04-23 10:00:00', 'shipped', 59.98, 'credit card', 'paid'),
        (1, '2024-04-23 10:15:00', 'pending', 14.99, 'paypal', 'pending'),
        (2, '2024-04-23 10:30:00', 'delivered', 199.96, 'credit card', 'paid'),
        (3, '2024-04-23 10:45:00', 'shipped', 4.99, 'paypal', 'paid'),
        (4, '2024-04-23 11:00:00', 'delivered', 49.98, 'credit card', 'paid'),
        (5, '2024-04-23 11:15:00', 'pending', 999.99, 'paypal', 'pending'),
        (1, '2024-04-23 11:30:00', 'shipped', 179.97, 'credit card', 'paid'),
        (2, '2024-04-23 11:45:00', 'delivered', 9.99, 'paypal', 'paid'),
        (3, '2024-04-23 12:00:00', 'pending', 79.98, 'credit card', 'pending'),
        (4, '2024-04-23 12:15:00', 'shipped', 2.99, 'cash on delivery', 'paid'),
        (5, '2024-04-23 12:30:00', 'delivered', 69.98, 'credit card', 'paid'),
        (1, '2024-04-23 12:45:00', 'shipped', 199.99, 'paypal', 'paid'),
        (2, '2024-04-23 13:00:00', 'delivered', 149.97, 'credit card', 'paid'),
        (3, '2024-04-23 13:15:00', 'pending', 69.99, 'cash on delivery', 'pending'),
        (4, '2024-04-23 13:30:00', 'shipped', 1999.98, 'credit card', 'paid'),
        (5, '2024-04-23 13:45:00', 'delivered', 49.99, 'paypal', 'paid'),
    ]

    # Insert hardcoded order data into the database
    for order in order_data:
        cursor.execute('''INSERT INTO orders (user_id, order_date, status, total_price, payment_method, payment_status)
                        VALUES (?, ?, ?, ?, ?, ?)''', order)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()    

create_orders_table(reset=True)
populate_orders_table()

@app.route('/orders/place', methods=['POST'])
def place_order():
    data = request.json
    user_id = data.get('user_id')
    order_lines = data.get('order_lines')
    payment_method = data.get('payment_method')
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = 'pending'  # Default status for newly placed orders
    payment_status = 'pending'  # Default payment status

    tax = 3 # The default tax rate
    total_price = sum(line['total_price'] * (1 + tax/100) for line in order_lines)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute('''INSERT INTO orders (user_id, order_date, status, total_price, payment_method, payment_status)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (user_id, current_date, status, total_price, payment_method, payment_status))
        new_order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return jsonify({'message': 'Order placed successfully', 'order_id': new_order_id}), 201
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/orders/update_status/<int:order_id>', methods=['PUT'])
def update_order_status(order_id):
    data = request.json
    status = data.get('status')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute('''UPDATE orders SET status=? WHERE order_id=?''', (status, order_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Order status updated successfully'}), 200
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order_by_id(order_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM orders WHERE id=?''', (order_id,))
    order = cursor.fetchone()
    conn.close()

    if order:
        order_data = {
            'order_id': order[0],
            'user_id': order[1],
            'order_date': order[2],
            'status': order[3],
            'total_price': order[4],
            'payment_method': order[5],
            'payment_status': order[6]
        }
        return jsonify(order_data), 200
    else:
        return jsonify({'error': 'Order not found'}), 404

@app.route('/orders/user/<int:user_id>', methods=['GET'])
def get_orders_by_user_id(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM orders WHERE user_id=?''', (user_id,))
    orders = cursor.fetchall()
    conn.close()

    order_list = []
    for order in orders:
        order_data = {
            'order_id': order[0],
            'user_id': order[1],
            'order_date': order[2],
            'status': order[3],
            'total_price': order[4],
            'payment_method': order[5],
            'payment_status': order[6]
        }
        order_list.append(order_data)

    return jsonify(order_list), 200

@app.route('/orders/status/<string:status>', methods=['GET'])
def get_orders_by_status(status):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM orders WHERE status=?''', (status,))
    orders = cursor.fetchall()
    conn.close()

    order_list = []
    for order in orders:
        order_data = {
            'order_id': order[0],
            'user_id': order[1],
            'order_date': order[2],
            'status': order[3],
            'total_price': order[4],
            'payment_method': order[5],
            'payment_status': order[6]
        }
        order_list.append(order_data)

    return jsonify(order_list), 200

@app.route('/orders/payment_status/<string:payment_status>', methods=['GET'])
def get_payment_status(payment_status):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM orders WHERE payment_status=?''', (payment_status,))
    orders = cursor.fetchall()
    conn.close()

    order_list = []
    for order in orders:
        order_data = {
            'order_id': order[0],
            'user_id': order[1],
            'order_date': order[2],
            'status': order[3],
            'total_price': order[4],
            'payment_method': order[5],
            'payment_status': order[6]
        }
        order_list.append(order_data)

    return jsonify(order_list), 200

@app.route('/orders/total_revenue', methods=['GET'])
def get_total_revenue():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT SUM(total_price) FROM orders WHERE payment_status='paid' ''')
    total_revenue = cursor.fetchone()[0]
    conn.close()

    return jsonify({'total_revenue': total_revenue}), 200

@app.route('/orders/cancel/<int:order_id>', methods=['PUT'])
def cancel_order(order_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute('''UPDATE orders SET status='cancelled' WHERE order_id=?''', (order_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Order cancelled successfully'}), 200
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/orders/accept/<int:order_id>', methods=['PUT'])
def accept_order(order_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute('''UPDATE orders SET status='accepted' WHERE order_id=?''', (order_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Order accepted successfully'}), 200
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='localhost', port=9053, debug=True)