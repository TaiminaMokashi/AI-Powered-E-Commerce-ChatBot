from flask import Flask, request, jsonify, render_template
import json
import os
import random

app = Flask(__name__)

PRODUCTS_PATH = 'data/products.json'

# --- List/Search Products ---
@app.route('/products', methods=['GET'])
def products():
    query = request.args.get('q', '').strip().lower()
    if not os.path.exists(PRODUCTS_PATH):
        return jsonify({'products': []}), 200
    with open(PRODUCTS_PATH, 'r') as f:
        products = json.load(f)
    if query:
        products = [p for p in products if query in p['name'].lower()]
    return jsonify({'products': products}), 200

# --- Chat Endpoint ---
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({'error': 'Message is required.'}), 400

    msg_lower = user_message.lower()
    bot_reply = "I'm not sure how to help with that. You can ask about products or say hi!"

    # Greeting intent
    if any(greet in msg_lower for greet in ['hello', 'hi', 'hey']):
        bot_reply = "Hello! How can I assist you today? You can ask about products or get recommendations."
    # Product search intent
    elif any(kw in msg_lower for kw in ['search', 'find', 'show me', 'look for', 'do you have']):
        for phrase in ['search', 'find', 'show me', 'look for', 'do you have']:
            if phrase in msg_lower:
                keyword = msg_lower.split(phrase)[-1].strip()
                break
        else:
            keyword = msg_lower.strip()
        # Search products
        if not os.path.exists(PRODUCTS_PATH):
            results = []
        else:
            with open(PRODUCTS_PATH, 'r') as f:
                products = json.load(f)
            results = [p for p in products if keyword in p['name'].lower()]
        if results:
            bot_reply = "Here are some products I found:\n" + "\n".join([f"- {r['name']} (₹{r['price']})" for r in results])
        else:
            bot_reply = "No products found matching your search."
    # Recommendation intent
    elif any(kw in msg_lower for kw in ['recommend', 'suggest', 'what should i buy', 'any suggestions', 'show recommendations']):
        if not os.path.exists(PRODUCTS_PATH):
            recs = []
        else:
            with open(PRODUCTS_PATH, 'r') as f:
                products = json.load(f)
            import random
            recs = random.sample(products, min(3, len(products)))
        if recs:
            bot_reply = "Here are some products you might like:\n" + "\n".join([f"- {r['name']} (₹{r['price']})" for r in recs])
        else:
            bot_reply = "No products to recommend right now."
    # Order tracking intent
    elif any(kw in msg_lower for kw in ['track', 'order status', 'where is my order', 'track my order']):
        import re
        match = re.search(r'order[\s#]*([A-Za-z0-9]+)', msg_lower)
        order_id = match.group(1) if match else None
        if order_id:
            ORDERS_PATH = 'data/orders.json'
            if os.path.exists(ORDERS_PATH):
                with open(ORDERS_PATH, 'r') as f:
                    orders = json.load(f)
                order = next((o for o in orders if o['order_id'].lower() == order_id.lower()), None)
                if order:
                    status = order.get('status', '')
                    # Remove 'Processing' and any trailing punctuation/whitespace
                    status = re.sub(r'[\s,.!]*Processing[.]*[\s,.!]*$', '', status, flags=re.IGNORECASE)
                    bot_reply = f"Order {order_id}: {status.strip()}"
                else:
                    bot_reply = f"Sorry, I couldn't find an order with ID {order_id}."
            else:
                bot_reply = "Order tracking is not available right now."
        else:
            bot_reply = "Please provide your order ID (e.g., 'track order #123456')."
    # Support/general issue intent
    elif any(kw in msg_lower for kw in ['issue', 'problem', 'help', 'support']):
        bot_reply = "I'm here to help! Please describe your issue, and I'll do my best to assist you or connect you with support."
    # Direct product name search
    else:
        if not os.path.exists(PRODUCTS_PATH):
            results = []
        else:
            with open(PRODUCTS_PATH, 'r') as f:
                products = json.load(f)
            results = [p for p in products if msg_lower in p['name'].lower()]
        if results:
            bot_reply = "Here are some products I found:\n" + "\n".join([f"- {r['name']} (₹{r['price']})" for r in results])
    return jsonify({'reply': bot_reply}), 200

@app.route('/create_order', methods=['POST'])
def create_order():
    data = request.get_json()
    products = data.get('products', [])
    if not products:
        return jsonify({'error': 'No products in order.'}), 400

    order_id = str(random.randint(100000, 999999))
    product_names = ', '.join([p['name'] for p in products])
    status = f"Order placed for {product_names}. Expected delivery in 2 days."

    # Optionally, save the order to a file (orders.json)
    ORDERS_PATH = 'data/orders.json'
    order_entry = {
        "order_id": order_id,
        "products": products,
        "status": status
    }
    if os.path.exists(ORDERS_PATH):
        with open(ORDERS_PATH, 'r') as f:
            orders = json.load(f)
    else:
        orders = []
    orders.append(order_entry)
    with open(ORDERS_PATH, 'w') as f:
        json.dump(orders, f, indent=2)

    return jsonify({
        "order_id": order_id,
        "products": products,
        "status": status
    }), 200

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
