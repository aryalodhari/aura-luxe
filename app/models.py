from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship

#user /customer account information 
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(225), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pincode = db.Column(db.String(10))
    country = db.Column(db.String(100), default="India")
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def set_password(self, password):
        """Hash and set password"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.username}>"
    
#contains product categories like bags,sunglasses etc..
class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    # slug = db.Column(db.String(120), nullable=False, unique=True) 
    description = db.Column(db.Text)
    image_url = db.Column(db.String(225))
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f"<Category {self.name}>"
    

#contains individual product information
class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    # slug = db.Column(db.String(220), nullable=False, unique=True)  
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    price = db.Column(db.Integer)
    quantity = db.Column(db.Integer, default=1)

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
    price = db.Column(db.Integer)

    # relation ship for the product
    product = relationship("Product", backref="cart_items")
    
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
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    #links the Order to its OrderItems
    items = relationship("OrderItem", backref="order", lazy=True)
    
    def __repr__(self):
        return f"<Order {self.order_number}>"
    

#contains items in each order
class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)  
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    product = relationship("Product", backref="orders")

    def __repr__(self):
        return f"<OrderItem Order {self.order_id} Product {self.product_id}>"
    

#contains product reviews and ratings
class Review (db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    title = db.Column(db.String(200))
    is_verified = db.Column(db.Boolean, default=False)
    helpful_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    user = relationship("User", backref="reviews")

    def __repr__(self):
        return f"<Review by User {self.user_id} For Product {self.product_id}>"
    
#contains Users wishlist/Favourite items
class WishList(db.Model):
    __tablename__ = "wishlists"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  
    added_at = db.Column(db.DateTime, default=db.func.now())
    
    def __repr__(self):
        return f"<WishList User {self.user_id} Product {self.product_id}>"
    
#contains Promocodes and Discounts
class DiscountCode(db.Model):
    __tablename__ = "discount_codes"
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    discount_type = db.Column(db.String(20))
    discount_value = db.Column(db.Float, nullable=False),
    discount_percent = db.Column(db.Integer)
    minimum_purchase = db.Column(db.Float, default=0)
    max_usage = db.Column(db.Integer)
    usage_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    valid_from = db.Column(db.DateTime)
    valid_until = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    def __repr__(self):
        return f"<DiscountCode {self.code}>"
    
#contains contact form messages
class ContactMessage(db.Model):
    __tablename__ = "contact_messages"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="unread")
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    def __repr__(self):
        return f"<ContactMessage from {self.email}>"
    
#--------------------------------------- Amin Models ----------------------------------------------
class AdminLog(db.Model):
    """Track every admin action for audit trail"""
    __tablename__ = "admin_logs"
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)  # 'create', 'update', 'delete'
    entity_type = db.Column(db.String(50), nullable=False)  # 'Product', 'Category', 'Order'
    entity_id = db.Column(db.Integer)  # ID of what was changed
    description = db.Column(db.Text)  # What changed
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    def __repr__(self):
        return f"<AdminLog {self.admin_id} - {self.action}>"
 
 
# ---------------------------------- DAILY SALES METRICS --------------------------------------
class SalesReport(db.Model):
    """Daily sales analytics for admin dashboard"""
    __tablename__ = "sales_reports"
    
    id = db.Column(db.Integer, primary_key=True)
    report_date = db.Column(db.Date, nullable=False, unique=True)
    total_orders = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Float, default=0)
    total_items_sold = db.Column(db.Integer, default=0)
    new_customers = db.Column(db.Integer, default=0)
    total_refunds = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    def __repr__(self):
        return f"<SalesReport {self.report_date}>"
 
 
# ----------------------------------------- STOCK TRACKING ---------------------------------------
class StockHistory(db.Model):
    """Track all stock changes for inventory management"""
    __tablename__ = "stock_history"
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    previous_quantity = db.Column(db.Integer)
    new_quantity = db.Column(db.Integer)
    change_type = db.Column(db.String(50), nullable=False)  # 'purchase', 'sale', 'adjustment'
    reason = db.Column(db.String(255))
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Who made change
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    def __repr__(self):
        return f"<StockHistory Product {self.product_id}>"
 
 
# -------------------------------- PRODUCT ANALYTICS --------------------------
class ProductAnalytics(db.Model):
    """Track product sales performance"""
    __tablename__ = "product_analytics"
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, unique=True)
    views_count = db.Column(db.Integer, default=0)  # How many viewed
    units_sold = db.Column(db.Integer, default=0)  # How many sold
    revenue = db.Column(db.Float, default=0)  # Total revenue from this product
    average_rating = db.Column(db.Float, default=0)
    total_reviews = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    def __repr__(self):
        return f"<ProductAnalytics Product {self.product_id}>"
 
 
# ----------------------------- REFUND MANAGEMENT ------------------------
class Refund(db.Model):
    """Track refund requests and processing"""
    __tablename__ = "refunds"
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    refund_amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected', 'processed'
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now())
    processed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f"<Refund Order {self.order_id}>"