from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone_number = db.Column(db.String(15), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    quantity_in_stock = db.Column(db.Integer, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))

    supplier = db.relationship('Supplier', back_populates='products')

    def __repr__(self):
        return f'<Product {self.name}>'


class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    
    products = db.relationship('Product', back_populates='supplier')

    def __repr__(self):
        return f'<Supplier {self.name}>'


class Sales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    name = db.Column(db.String(100), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    date_of_sale = db.Column(db.DateTime, default=db.func.current_timestamp())
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipt.id'))

    def __repr__(self):
        return f'<Sales {self.name}>'


class Receipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_amount = db.Column(db.Float, nullable=False)
    date_of_receipt = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Receipt {self.id}>'


class StockSummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    total_stock_value = db.Column(db.Float, nullable=False)
    total_sold_value = db.Column(db.Float, nullable=False)
    total_unsold_value = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<StockSummary {self.product_id}>'
