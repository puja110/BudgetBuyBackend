from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# List to store posted items
items = []

# POST API to create an item
@app.route('/api/item', methods=['POST'])
def create_item():
    data = request.get_json()
    
    # Validating the input
    required_fields = ['item_name', 'item_type', 'price', 'location', 'detail', 'quantity']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    item = {
        'item_name': data['item_name'],
        'item_type': data['item_type'],
        'price': data['price'],
        'location': data['location'],
        'detail': data['detail'],
        'quantity': data['quantity']
    }

    # Appending item to the list
    items.append(item)

    return jsonify(item), 201

# GET API to fetch all posted items
@app.route('/api/items', methods=['GET'])
def get_items():
    return jsonify(items)

# Web interface (HTML form) to post item
@app.route('/')
def index():
    return render_template('index.html')

# POST method for web interface to add item
@app.route('/submit_item', methods=['POST'])
def submit_item():
    item_name = request.form['item_name']
    item_type = request.form['item_type']
    price = request.form['price']
    location = request.form['location']
    detail = request.form['detail']
    quantity = request.form['quantity']

    item = {
        'item_name': item_name,
        'item_type': item_type,
        'price': price,
        'location': location,
        'detail': detail,
        'quantity': quantity
    }

    # Appending item to the list
    items.append(item)

    return render_template('index.html', items=items)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
