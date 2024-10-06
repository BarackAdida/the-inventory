import re
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone_number = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone_number": self.phone_number,
            "password_hash": self.password_hash
        }

    def set_password(self, password):
        if self.validate_password(password):
            self.password_hash = generate_password_hash(password)
        else:
            raise ValueError("Password must be at least 8 characters, include letters and numbers, and contain no special symbols")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def validate_email(email):
        if re.match(r'^[a-zA-Z0-9_.+-]+@gmail\.com$', email):
            return True
        else:
            raise ValueError("Email must end with '@gmail.com'.")

    @staticmethod
    def validate_phone_number(phone_number):
        if re.match(r'^\d{10}$', phone_number):
            return True
        else:
            raise ValueError("Phone number must be 10 digits.")

    @staticmethod
    def validate_password(password):
        if re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password):
            return True
        else:
            raise ValueError("Password must be at least 8 characters, include letters and numbers, and contain no special symbols")

    @staticmethod
    def validate_user(email, phone_number, password):
        User.validate_email(email)
        User.validate_phone_number(phone_number)
        User.validate_password(password)

product_supplier = db.Table('product_supplier',
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True),
    db.Column('supplier_id', db.Integer, db.ForeignKey('suppliers.id'), primary_key=True)
)

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    sku = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity_in_stock = db.Column(db.Integer, nullable=False)
    suppliers = db.relationship('Supplier', secondary=product_supplier, back_populates='products')

    stock_transactions = db.relationship('StockTransaction', backref='product', lazy=True)
    sales = db.relationship('Sale', backref='product', lazy=True)

    def get_current_quantity_in_stock(self):
        total_quantity_sold = sum(sale.quantity_sold for sale in self.sales)
        return self.quantity_in_stock - total_quantity_sold

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "sku": self.sku,
            "description": self.description,
            "price": self.price,
            "quantity_in_stock": self.quantity_in_stock
        }
    
class Supplier(db.Model):
    __tablename__ = "suppliers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    contact = db.Column(db.String, unique=True, nullable=False)

    products = db.relationship('Product', secondary=product_supplier, back_populates='suppliers')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "contact": self.contact
        }

class Sales(db.Model):
    __tablename__ = "sales"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    date_of_sale = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.id'), nullable=False)

    receipt = db.relationship('Receipt', backref=db.backref('sales', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "name": self.name,
            "quantity_sold": self.quantity_sold,
            "total_price": self.total_price,
            "date_of_sale": self.date_of_sale,
            "receipt_id": self.receipt_id
        }

class StockTransaction(db.Model):
    __tablename__ = "stock_transactions"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date_of_transaction = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    transaction_type = db.Column(db.String, nullable=False)

    product = db.relationship('Product', backref=db.backref('stock_transactions', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "date_of_transaction": self.date_of_transaction,
            "transaction_type": self.transaction_type
        }
    
class Receipt(db.Model):
    __tablename__ = "receipts"
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    date_of_receipt = db.Column(DateTime, default=datetime.utcnow, nullable=False)

    sale = db.relationship('Sales', backref='receipt')

    def to_dict(self):
        return {
            "id": self.id,
            "sale_id": self.sale_id,
            "total_amount": self.total_amount,
            "date_of_receipt": self.date_of_receipt
        }
    
class StockSummary(db.Model):
    __tablename__ = "stock_summary"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    total_stock_value = db.Column(db.Float, nullable=False, default=0.0)
    total_sold_value = db.Column(db.Float, nullable=False, default=0.0)
    total_unsold_value = db.Column(db.Float, nullable=False, default=0.0)
    
    product = db.relationship("Product", backref="stock_summary")

    def update_stock_values(self):
        product = Product.query.get(self.product_id)
        self.total_stock_value = product.quantity_in_stock * product.price
        total_sold = db.session.query(db.func.sum(Sales.total_price)).filter_by(product_id=self.product_id).scalar() or 0
        self.total_sold_value = total_sold
        self.total_unsold_value = self.total_stock_value - self.total_sold_value
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "total_stock_value": self.total_stock_value,
            "total_sold_value": self.total_sold_value,
            "total_unsold_value": self.total_unsold_value,
        }
