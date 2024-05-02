import requests
from datetime import datetime, timedelta

SERVER = "http://localhost:"
PORT_USER = "9050"
PORT_PRODUCT = "9051"
PORT_CART = "9052"
PORT_ORDER = "9053"
PORT_PAYMENT = "9054"

def check_user_exists(user_id):
    # Check if user_id exists
    user_response = requests.get(SERVER + PORT_USER + "/users/" + user_id)
    if user_response.status_code != 200:
        print("User does not exist.")
        return False
    return user_response

#flow-start(buy-app)
def buy_cart(user_id):
    user_id = str(user_id)

    user_response = check_user_exists(user_id)
    user_data = user_response.json()

    # Get all the cart lines associated with that user made in the last 24 hours
    cart_response = requests.get(SERVER + PORT_CART + "/cart/user/" + user_id)
    if cart_response.status_code != 200:
        print("Error retrieving cart lines.")
        return False

    cart_lines = cart_response.json()
    cart_lines_active = [line for line in cart_lines if line["status"] == "active"]

    # Filter cart lines made in the last 24 hours
    current_time = datetime.now()
    cart_lines_24h = [line for line in cart_lines_active if (current_time - datetime.strptime(line['date_added'], '%Y-%m-%d %H:%M:%S')) <= timedelta(hours=24)]

    if not cart_lines_24h:
        print("No cart lines found in the last 24 hours.")
        return False

    # Check if all the cart lines are still active
    for line in cart_lines_24h:
        if line['status'] != 'active':
            print("One or more cart lines are not active.")
            return False

    # Check if any of those products have been ordered in the last 5 minutes
    cart_lines_5min = [line for line in cart_lines_active if (current_time - datetime.strptime(line['date_added'], '%Y-%m-%d %H:%M:%S')) <= timedelta(minutes=5)]
    ordered_products_count = len(cart_lines_5min)

    # Call the cart microservice again and purchase the items in the cart
    purchase_response = requests.put(SERVER + PORT_CART + "/cart/purchase/" + user_id)
    if purchase_response.status_code != 200:
        print("Error purchasing items in the cart.")
        return False

    # Create a pending order with the current details through the order microservice
    order_data = {
        'user_id': user_id,
        'order_date': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'pending',
        'total_price': sum(line['total_price'] for line in cart_lines_24h),
        'payment_method': 'cash on delivery',
        'payment_status': 'pending'
    }

    create_order_response = requests.post(SERVER + PORT_ORDER + "/orders/place", json=order_data)
    if create_order_response.status_code != 201:
        print("Error creating pending order.")
        return False

    order_id = create_order_response.json().get('order_id')

    # Create a pending payment invitation through the payment microservice
    payment_data = {
        'order_id': order_id,
        'user_id': user_id,
        'payment_method': 'cash on delivery',  # Assuming user has a default payment method
        'amount': order_data['total_price'],
        'transaction_date': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'pending'
    }

    create_payment_response = requests.post(SERVER + PORT_PAYMENT + "/payments/process", json=payment_data)
    if create_payment_response.status_code != 201:
        print("Error creating pending payment invitation.")
        return False

    print("Purchase completed successfully.")
    return True

# Example usage
if __name__ == "__main__":
    status = buy_cart(1)
    print(status)