import re
from flask_sqlalchemy import SQLAlchemy, DateTime
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone_number = db.Column(db.String(100), nullable=False,unique=True)
    password_hash = db.Column(db.String(128), nullable=False)

    def to_dict(self):
        return{
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
            raise ValueError("Password must be at least 8 characters, a letter, numbers and no special symbols")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def validate_email(email):
        if re.match(r'^[a-zA-Z0-9_.+-]+@gmail\,com$', email):
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
             raise ValueError("Password must be at least 8 characters, a letter, numbers and no special symbols")


    @staticmethod
    def validate_user(self, email, phone_number, password):
        if not self.validate_email(email):
            raise ValueError("Invalid Email Format!")
        if not self.validate_phone_number(phone_number):
            raise ValueError("Invalid Phone Number Format!")
        if not self.validate_password(password):
            raise ValueError("Invalid Password Format!")
        
class Product(db.Model):
    __tablename__ = "products"
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String, unique=True, nullable=False)
    sku=db.Column(db.String, unique=True, nullable=False)
    description=db.Colum(db.String, nullable=False)
    price=db.Column(db.Float, nullable=False)
    quantity_in_stock=db.Column(db.Integer, nullable=False)
    supplier_id=db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return{
            "id":self.id,
            "name":self.name,
            "sku":self.sku,
            "description":self.description,
            "price":self.price,
            "quantity_in_stock":self.quantity_in_stock,
            "supplier_id":self.supplier_id
        }
    
class Supplier(db.Model):
    __tablename__ = "suppliers"
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String, unique=True, nullable=False)
    contact=db.column(db.string, unique=True, nullable=False)

    def to_dict(self):
        return{
            "id":self.id,
            "name":self.name,
            "contact":self.contact
        }
    
class Sale(db.Model):
    __tablename__ = "sales"
    id=db.Column(db.Integer, primary_key=True)
    product_id=db.Column(db.Integer, nullable=False)
    name=db.Calumn(db.String, nullable=False)
    quantity_sold=db.Column(db.Integer, nullable=False)
    total_price=db.Column(db.Float, nullable=False)
    date_of_sale=db.Column(DateTime, default=datetime.utcnow, nullable=False)
    receipt_id=db.Column(db.Integer, nullable=False)

    def to_dict(self):
        {
            "id":self.id,
            "product_id":self.product_id,
            "name":self.name,
            "quantity_sold":self.quantity_sold,
            "total_price":self.total_price,
            "date_of_sale":self.date_of_sale,
            "receipt_id":self.receipt_id
        }


    

