from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt
from config import get_config
import jwt
import re
import datetime
from functools import wraps
from models import db, User, Product

app = Flask(__name__)
app.config.from_object(get_config())
app.config['SECRET_KEY'] = 'HS256' 

#initialize extentions
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)
bcrypt = Bcrypt(app)

#initialize CORS with specific origin
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return 'Hello, this is an inventory designed by BARACK!'

@app.route('/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone_number = data.get('phone_number')
    password_hash = data.get('password_hash')

    #validate data 
    if not name or not email or not phone_number or not password_hash:
        return jsonify({'message': 'name, email,phone_number and password are required!'}), 400

    if User.query.filter_by(name=name).first():
        return jsonify({'message': 'name already exists!'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': "Email already exits"}), 400

    password_pattern = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$')
    if not password_pattern.match(password_hash):
        return jsonify({'message': 'Password must be at least 8 characters long and contain both letters and numbers.'}), 400

    #create user
    new_user = User(
        name=name,
        email=email,
        phone_number=phone_number,
        password_hash=bcrypt.generate_password_hash(password_hash).decode('utf-8')
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Your account has been created successfully🎉🎉'}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password_hash = data.get('password_hash')

    # Check if user exists and password is correct
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password_hash, password_hash):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({
            'access_token': token,
            'name': user.name,
            'id': user.id
        }), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

class ProductResource(Resource):
    def post(self, product_id):
        data = request.get_json()
        new_product = Product(
            name = data['name'],
            sku = data['sku'],
            description = data['description'],
            price = data['price'],
            quantity_in_stock = data['quantity_in_stock'],
            suppliers = data['supplier']
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': 'Product added successfully👍'}), 201
    
    def get(self, product_id):
        product = Product.query.get(product_id)
        if product:
            return jsonify({
                'name': product.name,
                'sku': product.sku,
                'description': product.description,
                'price': product.price,
                'quantity_in_stock': product.quantity_in_stock,
                'suppliers': product.suppliers
                }), 200
        return jsonify({'message': 'Product not found😒'}), 404
    
    def patch(self, product_id):
        product = Product.query.get(product_id)
        if product is None:
            return jsonify({'message': 'Product to be edited not found😒'}), 404
        
        data = request.get_json()
        if 'name' in data:
            product.name = data['name']
        if 'sku' in data:
            product.sku = data['sku']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = data['price']
        if 'quantity_in_stock' in data:
            product.quantity_in_stock = data['quantity_in_stock']
        if 'supplier' in data:
            product.supplier = data['supplier']

        db.session.commit()
        return jsonify({'message': 'Product updated successfully👍'}), 200
    
    def delete(self, product_id):
        product = Product.query.get(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
            return jsonify({'message': 'Product deleted successfully👍'}), 200
        
        return jsonify({'message': 'Product to be deleted not found😒'}), 404
    
api.add_resource(ProductResource, '/products' '/products/<int:product_id>')
    
if __name__ == '__main__':
    app.run(debug=True, port=5555)
