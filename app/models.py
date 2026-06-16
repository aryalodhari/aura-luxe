from app import db
from datetime import datetime

#user /customer account information 
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.string(100), nullabel=False, unique=True)
    email = db.Column(db.string(100), nullabel=False, unique=True)
    password = db.Column(db.string(225), nullabel=False)
    first_name = db.Column(db.string(100))
    last_name = db.Column(db.string(100))
    phone = db.Column(db.string(20))
    address = db.Column(db.Text)
    city = db.Column(db.string(100))
    state = db.Column(db.string(100))
    pincode = db.Column(db.string(10))
    country = db.Column(db.string(100), default="India")
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<User {self.username}>"
    
#contains product categories like bags,sunglasses etc..
class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.string(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    image_url = db.Column(db.string(225))
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f"<Category {self.name}>"
    

#contains individual product information
class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    cost_price = db.Column(db.Float)
    stock = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    image_url = db.Column(db.String(255))
    sku = db.Column(db.String(50), unique=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<Product {self.name}>"

    
#shopping cart for the user
class Cart(db.Model):
    __tablename__ = "carts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeginKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<Cart for user {self.user_id}>"
    
#contains items in shopping cart
class CartItem(db.Model):
    __tablename__ = "cart_items"
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=db.func.now())
    
    def __repr__(self):
        return f"<CartItem Product {self.product_id} x{self.quantity}>"
    

class Order(db.Model):
    __tablename__ = "orders"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_number = db.Column(db.String(50), unique=True)
    total_amount = db.Column(db.Float, nullable=False)
    discount_amount = db.Column(db.Float, default=0)
    final_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="pending")
    shipping_address = db.Column(db.Text)
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(20), default="pending")
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    def __repr__(self):
        return f"<Order {self.order_number}>"


