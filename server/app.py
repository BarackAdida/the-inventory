import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt
from config import get_config
from models import db, User, Product, Supplier, Sales, Receipt, StockSummary
import jwt
import re
import datetime
from functools import wraps

app = Flask(__name__)
app.config.from_object(get_config())
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_default_secret_key') 

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)
bcrypt = Bcrypt(app)

# Initialize CORS with specific origin
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

    # Validate data 
    if not name or not email or not phone_number or not password_hash:
        return jsonify({'message': 'name, email, phone_number and password are required!'}), 400

    if User.query.filter_by(name=name).first():
        return jsonify({'message': 'name already exists!'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': "Email already exists"}), 400

    password_pattern = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$')
    if not password_pattern.match(password_hash):
        return jsonify({'message': 'Password must be at least 8 characters long and contain both letters and numbers.'}), 400

    # Create user
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
    def post(self):
        data = request.get_json()
        new_product = Product(
            name=data['name'],
            sku=data['sku'],
            description=data['description'],
            price=data['price'],
            quantity_in_stock=data['quantity_in_stock'],
            supplier_id=data.get('supplier_id')  # Ensure to match the correct attribute
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
                'supplier_id': product.supplier_id  # Match the correct attribute
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
        if 'supplier_id' in data:
            product.supplier_id = data['supplier_id']  # Update the supplier reference

        db.session.commit()
        return jsonify({'message': 'Product updated successfully👍'}), 200
    
    def delete(self, product_id):
        product = Product.query.get(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
            return jsonify({'message': 'Product deleted successfully👍'}), 200
        
        return jsonify({'message': 'Product to be deleted not found😒'}), 404
    
class SupplierResource(Resource):
    def get(self, supplier_id):
        supplier = Supplier.query.get(supplier_id)
        if supplier:
            return jsonify({
                'name': supplier.name,
                'contact': supplier.contact,
            }), 200
        return jsonify({'message': 'Supplier not found😒'}), 404
    
    def post(self):
        data = request.get_json()
        new_supplier = Supplier(name=data['name'], contact=data['contact'])
        db.session.add(new_supplier)
        db.session.commit()
        return jsonify({'message': 'Supplier created successfully👍'}), 201
    
    def delete(self, supplier_id):
        supplier = Supplier.query.get(supplier_id)
        if supplier:
            db.session.delete(supplier)
            db.session.commit()
            return jsonify({'message': 'Supplier deleted successfully👍'}), 200
        return jsonify({'message': 'Supplier to be deleted not found😒'}), 404
    
class SaleResource(Resource):
    def post(self):
        data = request.get_json()
        product = Product.query.get(data['product_id'])
        
        if not product:
            return jsonify({'message': 'Product not found😒'}), 404
        
        if product.quantity_in_stock < data['quantity_sold']:
            return jsonify({'message': 'Insufficient stock available😒'}), 400
        
        # Create a new sale
        new_sale = Sales(
            product_id=data['product_id'],
            name=product.name,
            quantity_sold=data['quantity_sold'],
            total_price=product.price * data['quantity_sold']
        )
        
        db.session.add(new_sale)
        
        # Update stock
        product.quantity_in_stock -= data['quantity_sold']
        
        # Create/update receipt
        receipt = Receipt(total_amount=new_sale.total_price)
        db.session.add(receipt)
        
        # Update stock summary
        stock_summary = StockSummary.query.filter_by(product_id=data['product_id']).first()
        if stock_summary:
            stock_summary.total_stock_value -= product.price * data['quantity_sold']
            stock_summary.total_sold_value += new_sale.total_price
        else:
            stock_summary = StockSummary(
                product_id=data['product_id'],
                total_stock_value=-1 * product.price * data['quantity_sold'],
                total_sold_value=new_sale.total_price,
                total_unsold_value=product.price * product.quantity_in_stock
            )
            db.session.add(stock_summary)

        db.session.commit()
        return jsonify({'message': 'Sale recorded successfully! 🎉', 'sale_id': new_sale.id}), 201
    
    def get(self, sale_id):
        sale = Sales.query.get(sale_id)
        if sale:
            return jsonify({
                'product_id': sale.product_id,
                'name': sale.name,
                'quantity_sold': sale.quantity_sold,
                'total_price': sale.total_price,
                'date_of_sale': sale.date_of_sale,
                'receipt_id': sale.receipt_id,
            }), 200
        return jsonify({'message': 'Sale not found😒'}), 404


# Add the resources to the API
api.add_resource(ProductResource, '/products', '/products/<int:product_id>')
api.add_resource(SupplierResource, '/suppliers', '/suppliers/<int:supplier_id>')
api.add_resource(SaleResource, '/sales', '/sales/<int:sale_id>')

if __name__ == '__main__':
    app.run(debug=True)
