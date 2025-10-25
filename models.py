from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    username = db.Column(db.String(150), unique=True, nullable=False)  
    email = db.Column(db.String(150), unique=True, nullable=False)  
    password_hash = db.Column(db.String(200), nullable=False)  
    is_admin = db.Column(db.Boolean, default=False, nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  

    # secure pasword
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False) 
    product_type = db.Column(db.String(100), nullable=False)      
    sizes = db.Column(db.String(200), nullable=True)      
    color = db.Column(db.String(100), nullable=True)      
    stock = db.Column(db.String(50), nullable=False, default="In Stock")  
    image_filename = db.Column(db.String(300), nullable=True)


class Order(db.Model):   
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    payment = db.Column(db.String(20), nullable=False, default="COD")
    total = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
