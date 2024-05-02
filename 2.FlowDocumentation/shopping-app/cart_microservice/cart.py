from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)


current_file_location = os.path.dirname(__file__)

DATABASE = os.path.join(current_file_location, 'cart.db')

def create_cart_table(reset=False):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if reset:
        cursor.execute('''DROP TABLE IF EXISTS cart''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS cart
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_id INTEGER NOT NULL,
                       product_id INTEGER NOT NULL,
                       quantity INTEGER NOT NULL,
                       price REAL NOT NULL,
                       total_price REAL NOT NULL,
                       date_added TEXT NOT NULL,
                       status TEXT NOT NULL,
                       session_id TEXT)''')
    conn.commit()
    conn.close()

def populate_cart_table():
    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    current_time = datetime.now()
    current_time = current_time.replace(microsecond=0)
    current_time = str(current_time)

    # List of hardcoded cart data
    cart_data = [
    # id, user_id, product_id, quantity, price,   total_price,  date_added,            status,  session_id
        (1,         3,          2,       599.99,   1199.98,    current_time, 'active', None),
        (2, 2, 1, 19.99, 19.99, current_time, 'active', None),
        (3, 4, 3, 39.99, 119.97, current_time, 'active', None),
        (4, 7, 1, 89.99, 89.99, current_time, 'active', None),
        (5, 5, 2, 29.99, 59.98, current_time, 'active', None),
        (6, 1, 1, 14.99, 14.99, current_time, 'active', None),
        (7, 8, 4, 49.99, 199.96, current_time, 'active', None),
        (8, 3, 1, 4.99, 4.99, current_time, 'active', None),
        (9, 6, 2, 24.99, 49.98, current_time, 'active', None),
        (10, 2, 1, 999.99, 999.99, current_time, 'active', None),
        (11, 5, 3, 59.99, 179.97, current_time, 'active', None),
        (12, 9, 1, 9.99, 9.99, current_time, 'active', None),
        (13, 10, 2, 39.99, 79.98, current_time, 'active', None),
        (14, 4, 1, 2.99, 2.99, current_time, 'active', None),
        (15, 7, 2, 34.99, 69.98, current_time, 'active', None),
        (16, 1, 1, 199.99, 199.99, current_time, 'active', None),
        (17, 8, 3, 49.99, 149.97, current_time, 'active', None),
        (18, 6, 1, 69.99, 69.99, current_time, 'active', None),
        (19, 3, 2, 999.99, 1999.98, current_time, 'active', None),
        (20, 9, 1, 49.99, 49.99, current_time, 'active', None),
    ]

    # Insert hardcoded cart data into the database
    for item in cart_data:
        cursor.execute('''INSERT INTO cart (user_id, product_id, quantity, price, total_price, date_added, status, session_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', item)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

create_cart_table(reset=True)
populate_cart_table()

@app.route('/cart/add', methods=['POST', 'PUT'])
def add_item_to_cart():
    data = request.json
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    price = data.get('price')
    date_added = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = 'active'  # Default status for newly added items

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute('''INSERT INTO cart (user_id, product_id, quantity, price, total_price, date_added, status)
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (user_id, product_id, quantity, price, price * quantity, date_added, status))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Item added to cart successfully'}), 201
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/cart/update/<int:item_id>', methods=['PUT'])
def update_item_in_cart(item_id):
    data = request.json
    quantity = data.get('quantity')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute('''UPDATE cart SET quantity=?, total_price=quantity*price WHERE id=?''', (quantity, item_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Item updated in cart successfully'}), 200
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/cart/remove/<int:item_id>', methods=['DELETE'])
def remove_item_from_cart(item_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute('''DELETE FROM cart WHERE id=?''', (item_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Item removed from cart successfully'}), 200
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/cart/items/<int:user_id>', methods=['GET'])
def get_cart_items(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM cart WHERE user_id=?''', (user_id,))
    items = cursor.fetchall()
    conn.close()

    item_list = []
    for item in items:
        item_data = {
            'id': item[0],
            'user_id': item[1],
            'product_id': item[2],
            'quantity': item[3],
            'price': item[4],
            'total_price': item[5],
            'date_added': item[6],
            'status': item[7],
            'session_id': item[8]
        }
        item_list.append(item_data)

    return jsonify(item_list), 200

@app.route('/cart/total_price/<int:user_id>', methods=['GET'])
def get_total_price(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT SUM(total_price) FROM cart WHERE user_id=?''', (user_id,))
    total_price = cursor.fetchone()[0]
    conn.close()

    return jsonify({'total_price': total_price}), 200

@app.route('/cart/user/<int:user_id>', methods=['GET'])
def get_cart_by_user_id(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM cart WHERE user_id=?''', (user_id,))
    cart_items = cursor.fetchall()
    conn.close()

    cart_data = []
    for item in cart_items:
        cart_item = {
            'id': item[0],
            'user_id': item[1],
            'product_id': item[2],
            'quantity': item[3],
            'price': item[4],
            'total_price': item[5],
            'date_added': item[6],
            'status': item[7],
            'session_id': item[8]
        }
        cart_data.append(cart_item)

    return jsonify(cart_data), 200

@app.route('/cart/purchase/<int:user_id>', methods=['PUT'])
def purchase_cart(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute('''UPDATE cart SET status='purchased' WHERE user_id=? AND status='active' ''', (user_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Cart purchased successfully'}), 200
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='localhost', port=9052, debug=True)