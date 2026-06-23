from app import create_app, db
from app.models import (
    User, Category, Product, Cart, 
    DiscountCode, ContactMessage
)
from werkzeug.security import generate_password_hash
from datetime import datetime

# create product
