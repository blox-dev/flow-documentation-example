from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

current_file_location = os.path.dirname(__file__)

DATABASE = os.path.join(current_file_location, 'products.db')

def create_products_table(reset=False):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if reset:
        cursor.execute('''DROP TABLE IF EXISTS products''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS products
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT NOT NULL,
                       description TEXT,
                       category TEXT NOT NULL,
                       price REAL NOT NULL,
                       available_quantity INTEGER NOT NULL)''')
    conn.commit()
    conn.close()

def populate_products_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # List of hardcoded product data
    product_data = [
    # id, name,        description,                                           category,    price, available_quantity
        ("Smartphone", "High-performance smartphone with advanced features", "Electronics", 599.99, 50),
        ("Men's T-shirt", "Comfortable cotton T-shirt for men", "Clothing", 19.99, 100),
        ("Python Programming Book", "Comprehensive guide to Python programming", "Books", 39.99, 30),
        ("Coffee Maker", "Automatic coffee maker for brewing delicious coffee", "Home & Kitchen", 89.99, 20),
        ("Yoga Mat", "Non-slip yoga mat for comfortable yoga sessions", "Sports & Outdoors", 29.99, 40),
        ("Lipstick", "Long-lasting lipstick in vibrant shades", "Beauty", 14.99, 80),
        ("Toy Car", "Remote-controlled toy car for kids", "Toys", 49.99, 60),
        ("Chocolate Bar", "Delicious milk chocolate bar", "Food", 4.99, 200),
        ("Multivitamin Tablets", "Daily multivitamin tablets for overall health", "Health", 24.99, 150),
        ("Laptop", "High-performance laptop for work and entertainment", "Electronics", 999.99, 30),
        ("Women's Dress", "Elegant dress for women for special occasions", "Clothing", 59.99, 80),
        ("Cookware Set", "Complete cookware set for your kitchen", "Home & Kitchen", 149.99, 10),
        ("Running Shoes", "Comfortable running shoes for men and women", "Sports & Outdoors", 79.99, 50),
        ("Shampoo", "Moisturizing shampoo for healthy hair", "Beauty", 9.99, 120),
        ("Board Game", "Classic board game for family fun", "Toys", 39.99, 70),
        ("Granola Bars", "Healthy snack bars with oats and nuts", "Food", 2.99, 300),
        ("Protein Powder", "Premium protein powder for muscle recovery", "Health", 34.99, 40),
        ("Smartwatch", "Feature-rich smartwatch with fitness tracking", "Electronics", 199.99, 20),
        ("Men's Jeans", "Stylish jeans for men in various sizes", "Clothing", 49.99, 90),
        ("Blender", "Powerful blender for making smoothies and shakes", "Home & Kitchen", 69.99, 25),
    ]

    # Insert hardcoded product data into the database
    for product in product_data:
        cursor.execute('''INSERT INTO products (name, description, category, price, available_quantity)
                        VALUES (?, ?, ?, ?, ?)''', product)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

create_products_table(reset=True)
populate_products_table()

@app.route('/products/add', methods=['POST'])
def add_product():
    data = request.json
    name = data.get('name')
    description = data.get('description')
    category = data.get('category')
    price = data.get('price')
    available_quantity = data.get('available_quantity')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute('''INSERT INTO products (name, description, category, price, available_quantity)
                          VALUES (?, ?, ?, ?, ?)''',
                       (name, description, category, price, available_quantity))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Product added successfully'}), 201
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/products/update/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    name = data.get('name')
    description = data.get('description')
    category = data.get('category')
    price = data.get('price')
    available_quantity = data.get('available_quantity')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute('''UPDATE products SET name=?, description=?, category=?, price=?, available_quantity=?
                          WHERE id=?''',
                       (name, description, category, price, available_quantity, product_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Product updated successfully'}), 200
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM products WHERE id=?''', (product_id,))
    product = cursor.fetchone()
    conn.close()

    if product:
        product_data = {
            'id': product[0],
            'name': product[1],
            'description': product[2],
            'category': product[3],
            'price': product[4],
            'available_quantity': product[5]
        }
        return jsonify(product_data), 200
    else:
        return jsonify({'error': 'Product not found'}), 404

@app.route('/products/category/<string:category>', methods=['GET'])
def get_products_by_category(category):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM products WHERE category=?''', (category,))
    products = cursor.fetchall()
    conn.close()

    product_list = []
    for product in products:
        product_data = {
            'id': product[0],
            'name': product[1],
            'description': product[2],
            'category': product[3],
            'price': product[4],
            'available_quantity': product[5]
        }
        product_list.append(product_data)

    return jsonify(product_list), 200

@app.route('/products/price_range', methods=['GET'])
def get_products_by_price_range():
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM products WHERE price BETWEEN ? AND ?''', (min_price, max_price))
    products = cursor.fetchall()
    conn.close()

    product_list = []
    for product in products:
        product_data = {
            'id': product[0],
            'name': product[1],
            'description': product[2],
            'category': product[3],
            'price': product[4],
            'available_quantity': product[5]
        }
        product_list.append(product_data)

    return jsonify(product_list), 200

@app.route('/products/search', methods=['GET'])
def search_products():
    query = request.args.get('query')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM products WHERE name LIKE ? OR description LIKE ?''', ('%' + query + '%', '%' + query + '%'))
    products = cursor.fetchall()
    conn.close()

    product_list = []
    for product in products:
        product_data = {
            'id': product[0],
            'name': product[1],
            'description': product[2],
            'category': product[3],
            'price': product[4],
            'available_quantity': product[5]
        }
        product_list.append(product_data)

    return jsonify(product_list), 200

if __name__ == '__main__':
    app.run(host='localhost', port=9051, debug=True)