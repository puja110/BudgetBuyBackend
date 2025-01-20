from flask import Flask, render_template, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Secret key to encode the JWT token
app.config['JWT_SECRET_KEY'] = 'a5fc&hA82@9p$^Y!dD0wQb9Dh5zJ1'
jwt = JWTManager(app)

users = []

items = [] # List to store posted items
item_id_counter = 1 # Unique id for item

# Helper function to find a user by username
def find_user(username):
    return next((user for user in users if user['username'] == username), None)

# Route for User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check if user already exists
    if find_user(username):
        return jsonify({"message": "User already exists"}), 400

    # Hash the password
    hashed_password = generate_password_hash(password, method='sha256')

    # Save user to the in-memory "database"
    users.append({
        'username': username,
        'password': hashed_password
    })

    return jsonify({"message": "User created successfully"}), 201

# Route for User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = find_user(username)
    
    if not user or not check_password_hash(user['password'], password):
        return jsonify({"message": "Invalid credentials"}), 401

    # Create JWT token
    access_token = create_access_token(identity=username)
    return jsonify({"access_token": access_token}), 200

# Protected Route Example (only accessible with a valid JWT token)
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    # Get current logged in user from the token
    current_user = get_jwt_identity()
    return jsonify({"message": f"Welcome {current_user}, this is a protected route!"}), 200

# POST API to create an item
@app.route('/api/item', methods=['POST'])
@jwt_required()
def create_item():
    global item_id_counter
    data = request.get_json()
    
    # Validating the input
    required_fields = ['item_name', 'item_type', 'price', 'location', 'detail', 'quantity']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    item = {
        'id': item_id_counter,
        'item_name': data['item_name'],
        'item_type': data['item_type'],
        'price': data['price'],
        'location': data['location'],
        'detail': data['detail'],
        'quantity': data['quantity']
    }

    # Appending item to the list
    items.append(item)
    item_id_counter += 1
    
    return jsonify(item), 201

# GET API to fetch all posted items
@app.route('/api/items', methods=['GET'])
@jwt_required()
def get_items():
    return jsonify(items)

# GET API to find an item by its ID
@app.route('/api/item/<int:item_id>', methods=['GET'])
@jwt_required()
def find_item(item_id):
    item = next((item for item in items if item['id'] == item_id), None)
    if item:
        return jsonify(item)
    return jsonify({'error': 'Item not found'}), 404

# PUT API to update an item by ID
@app.route('/api/item/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_item(item_id):
    data = request.get_json()

    # Find the item by ID
    item = next((item for item in items if item['id'] == item_id), None)
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    # Update the item's fields
    item['item_name'] = data.get('item_name', item['item_name'])
    item['item_type'] = data.get('item_type', item['item_type'])
    item['price'] = data.get('price', item['price'])
    item['location'] = data.get('location', item['location'])
    item['detail'] = data.get('detail', item['detail'])
    item['quantity'] = data.get('quantity', item['quantity'])

    return jsonify(item)

# DELETE API to delete an item by ID
@app.route('/api/item/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    global items
    
    # Find the item by ID
    item = next((item for item in items if item['id'] == item_id), None)
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    # Remove the item from the list
    items = [i for i in items if i['id'] != item_id]

    return jsonify({'message': 'Item deleted successfully'}), 200

# Web interface (HTML form) to post item
@app.route('/')
def index():
    return render_template('index.html')

# POST method for web interface to add item
@app.route('/submit_item', methods=['POST'])
def submit_item():
    global item_id_counter
    item_name = request.form['item_name']
    item_type = request.form['item_type']
    price = request.form['price']
    location = request.form['location']
    detail = request.form['detail']
    quantity = request.form['quantity']

    item = {
        'id': item_id_counter,  # Assign unique ID
        'item_name': item_name,
        'item_type': item_type,
        'price': price,
        'location': location,
        'detail': detail,
        'quantity': quantity
    }

    # Appending item to the list
    items.append(item)

    item_id_counter += 1

    return render_template('index.html', items=items)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
